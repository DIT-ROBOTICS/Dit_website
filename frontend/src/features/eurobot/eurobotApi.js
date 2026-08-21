export const eurobotApi = {
    latest: '/api/Eurobot',
    history: '/api/Eurobot/History',
    historyBackground: '/api/Eurobot/History/Background',
    introduction: '/api/Eurobot/Introduction',
    whiteRobotDetails: '/api/PopUpItem/whiteSeeMore',

    year(year) {
        return `/api/Eurobot/${year}`
    },
}

