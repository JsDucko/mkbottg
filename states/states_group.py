from aiogram.dispatcher.filters.state import State, StatesGroup

class Form(StatesGroup):
    WAITING_FOR_ANSWER = State()
    waiting_for_txt = State()
    WAITING_FOR_ANSWER_NUM = State()
    waiting_for_balance = State()
    main_menu = State()
    waiting_for_invest = State()
    waiting_for_balance_qiwi = State()
    waiting_for_currency = State()
    waiting_for_payment = State()
    waiting_for_withdraw = State()
    waiting_for_requisites = State()
    waiting_for_confirmation = State()
    waiting_for_balance_cryptobot = State()
    amount = State()
    waiting_for_balance_calculator = State()
    waiting_for_add_funds = State()
    
    

class ReviewStates(StatesGroup):
    Text = State()
    ConfirmText = State()
    Photo = State()
    ConfirmPhoto = State()
    Publish = State()