import { onBeforeUnmount, ref } from 'vue'

/**
 * useApiData：統一管理 Vue 元件中的 API 資料、載入、錯誤、重試與取消狀態。
 *
 * --------------------------------------------------------------------------
 * 1. 最基本的 JSON GET 請求
 * --------------------------------------------------------------------------
 *
 * script 中的 data/loading/error 都是 ref，因此讀值要使用 `.value`；
 * template 會自動解開 ref，不需要 `.value`。
 *
 * @example
 * const {
 *     data: sponsors,
 *     loading,
 *     error,
 *     load,
 *     reload,
 * } = useApiData([])
 *
 * onMounted(() => {
 *     load('/api/Sponsors')
 * })
 *
 * // script：sponsors.value
 * // template：sponsors
 *
 * template 可搭配 ApiState：
 *
 * <ApiState
 *     :loading="loading"
 *     :error="error"
 *     :empty="sponsors.length === 0"
 *     @retry="reload"
 * >
 *     <article v-for="sponsor in sponsors" :key="sponsor.id">
 *         {{ sponsor.name }}
 *     </article>
 * </ApiState>
 *
 * --------------------------------------------------------------------------
 * 2. initialValue（初始值）
 * --------------------------------------------------------------------------
 *
 * initialValue 應與 API 最後回傳的資料形狀一致，這樣第一次 render 時不會
 * 因為 undefined 而出錯。
 *
 * @example
 * useApiData([])                         // API 回傳陣列
 * useApiData({})                         // API 回傳物件
 * useApiData({ contacts: [], links: [] }) // 已知完整資料形狀
 * useApiData(null)                       // 尚未載入前不應有資料
 *
 * --------------------------------------------------------------------------
 * 3. 傳入 fetch 選項
 * --------------------------------------------------------------------------
 *
 * load() 的第二個參數除了 transform 之外，都會傳給原生 fetch()，因此可以
 * 使用 method、headers、body、credentials 等標準選項。signal 由本 composable
 * 自動管理，不需要自行傳入。
 *
 * @example
 * load('/api/example', {
 *     method: 'POST',
 *     headers: { 'Content-Type': 'application/json' },
 *     body: JSON.stringify({ name: 'DIT' }),
 * })
 *
 * --------------------------------------------------------------------------
 * 4. transform（回傳資料轉換）
 * --------------------------------------------------------------------------
 *
 * transform 會在 response.json() 後、寫入 data 前執行。可以取出部分欄位、
 * 排序、補預設值，也可以回傳 Promise。第二個參數包含原始 response 與
 * AbortSignal，適合進行第二階段請求。
 *
 * @example
 * load('/api/Sponsors', {
 *     transform: (json) => json.sponsors ?? [],
 * })
 *
 * @example
 * load('/api/Eurobot/History', {
 *     transform: async (urls, { signal }) => {
 *         return Promise.all(urls.map(async (url) => {
 *             const response = await fetch(url, { signal })
 *             if (!response.ok) throw new Error(`HTTP ${response.status}`)
 *             return response.json()
 *         }))
 *     },
 * })
 *
 * --------------------------------------------------------------------------
 * 5. run（自訂請求流程，並允許 reload）
 * --------------------------------------------------------------------------
 *
 * load() 固定把回應解析為 JSON；需要同時讀取文字和 JSON、組合多個 API，
 * 或使用非標準流程時使用 run()。callback 必須回傳最後要寫入 data 的資料。
 * run() 會記住 callback，因此 reload() 可以重新執行完整流程。
 *
 * @example
 * run(async (signal) => {
 *     const [textResponse, dataResponse] = await Promise.all([
 *         fetch('/api/introduction', { signal }),
 *         fetch('/api/data', { signal }),
 *     ])
 *
 *     if (!textResponse.ok || !dataResponse.ok) {
 *         throw new Error('資料載入失敗')
 *     }
 *
 *     return {
 *         introduction: await textResponse.text(),
 *         details: await dataResponse.json(),
 *     }
 * })
 *
 * --------------------------------------------------------------------------
 * 6. execute（底層執行器）
 * --------------------------------------------------------------------------
 *
 * execute() 和 run() 一樣接收自訂 callback，但 execute() 不會把請求記錄為
 * 可重試操作，因此之後呼叫 reload() 不會重跑這次 execute。一般元件優先
 * 使用 load() 或 run()；只有刻意不希望 reload 記住該操作時才直接使用它。
 *
 * --------------------------------------------------------------------------
 * 7. reload 與 abort
 * --------------------------------------------------------------------------
 *
 * reload()：重做最近一次 load() 或 run()。尚未請求過時回傳 undefined。
 * abort()：取消目前請求。取消屬於正常流程，不會寫入 error。
 *
 * 每次開始新請求時，上一個未完成請求會自動取消，避免較舊的回應覆蓋新資料。
 * 元件卸載時也會由 onBeforeUnmount 自動 abort，通常不必手動清理。
 *
 * --------------------------------------------------------------------------
 * 8. 回傳成員
 * --------------------------------------------------------------------------
 *
 * data    Ref：initialValue 或最後一次成功請求的結果。
 * loading Ref<boolean>：請求進行中為 true，完成、失敗或取消後為 false。
 * error   Ref<Error|null>：最後一次非取消錯誤；新請求開始時會清空。
 * load    Function：執行 JSON API 請求並記錄為可重試請求。
 * run     Function：執行自訂請求流程並記錄為可重試請求。
 * execute Function：執行自訂流程，但不更新 reload 所記住的請求。
 * reload  Function：重新執行最近一次 load 或 run。
 * abort   Function：手動取消目前請求。
 *
 * @param {*} initialValue API 尚未完成前使用的初始資料。
 * @returns {{
 *   data: import('vue').Ref,
 *   loading: import('vue').Ref<boolean>,
 *   error: import('vue').Ref<Error|null>,
 *   load: Function,
 *   run: Function,
 *   execute: Function,
 *   reload: Function,
 *   abort: Function
 * }}
 */
export function useApiData(initialValue = null) {
    const data = ref(initialValue)
    const loading = ref(false)
    const error = ref(null)

    let activeController = null
    let lastRequest = null

    /**
     * 執行具取消與狀態管理的底層請求，但不改變 reload 記錄。
     * @param {(signal: AbortSignal) => Promise<*>} request
     * @returns {Promise<* | null>} 成功結果；失敗或取消時為 null。
     */
    async function execute(request) {
        activeController?.abort()
        const controller = new AbortController()
        activeController = controller
        loading.value = true
        error.value = null

        try {
            const result = await request(controller.signal)
            if (!controller.signal.aborted) data.value = result
            return result
        } catch (requestError) {
            if (requestError.name !== 'AbortError') {
                error.value = requestError
                console.error('API request failed:', requestError)
            }
            return null
        } finally {
            if (activeController === controller) {
                loading.value = false
                activeController = null
            }
        }
    }

    /**
     * 請求 JSON API，並將解析、轉換後的結果存入 data。
     * @param {string | URL | Request} url
     * @param {RequestInit & { transform?: Function }} options
     * @returns {Promise<* | null>}
     */
    async function load(url, options = {}) {
        const { transform = (value) => value, ...fetchOptions } = options
        lastRequest = () => load(url, options)

        return execute(async (signal) => {
            const response = await fetch(url, { ...fetchOptions, signal })
            if (!response.ok) throw new Error(`HTTP ${response.status}: ${url}`)
            return transform(await response.json(), { response, signal })
        })
    }

    /**
     * 執行並記住自訂請求流程，使 reload 可以再次執行。
     * @param {(signal: AbortSignal) => Promise<*>} request
     * @returns {Promise<* | null>}
     */
    function run(request) {
        lastRequest = () => run(request)
        return execute(request)
    }

    /** 重新執行最近一次 load 或 run。 */
    function reload() {
        return lastRequest?.()
    }

    /** 取消目前進行中的請求；取消不會被視為錯誤。 */
    function abort() {
        activeController?.abort()
    }

    onBeforeUnmount(abort)

    return { data, loading, error, load, run, execute, reload, abort }
}
