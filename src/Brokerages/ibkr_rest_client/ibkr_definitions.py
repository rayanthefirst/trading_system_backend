from Enums.securities_definitions import TradableSecurity
from Enums.order_definitions import OrderTIF, TrailingStopType, OrderState

IBKRTradableSecurity = {
    TradableSecurity.STOCK: "stk",
    TradableSecurity.OPTION: "opt",
    TradableSecurity.FOREX: "cash",
}

IBKROrderTIF = {
    OrderTIF.DAY: "DAY",
    OrderTIF.GOOD_TILL_CANCELLED: "GTC",
}

IBKRTrailingStopType = {
    TrailingStopType.AMOUNT: "amt",
    TrailingStopType.PERCENTAGE: "%",
}

IBKROrderStatus = {
    OrderState.SUBMITTED: "submitted",
    OrderState.FILLED: "filled",
    OrderState.CANCELLED: "cancelled",
    OrderState.PENDING_CANCEL: "pending_cancel",
    OrderState.PENDING_SUBMIT: "pending_submit",
    OrderState.PRE_SUBMITTED: "pre_submitted",
    OrderState.INACTIVE: "inactive",
}
