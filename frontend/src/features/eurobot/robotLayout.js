/**
 * 根據機器人總數及其陣列索引，決定 3D Viewer 的初始觀看側。
 *
 * 偶數總數：第 1、3、5 台為 left，第 2、4、6 台為 right。
 * 奇數總數：第 1 台為 left；其後第 2、4、6 台為 left，第 3、5、7 台為 right。
 */
export function getRobotInitialViewSide(index, total) {
    const position = index + 1

    if (total % 2 === 0) {
        return position % 2 === 1 ? 'left' : 'right'
    }

    if (position === 1) return 'left'
    return position % 2 === 0 ? 'left' : 'right'
}

