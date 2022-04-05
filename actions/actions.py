from typing import Any, Text, Dict, List

from rasa_sdk.types import DomainDict
from rasa_sdk.events import EventType
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction

# 需要 rasa run actions 来启动
SERVICE_TYPES = {  ##TODO, name, and possible resource for dataset for 业务
    # 现在完成两个service，用中文作为intent name
    "选基金":
        {
            "name": "帮我选基金",
        },
    "基金":
        {
            "name": "基金查询",
        }
}


class ActionDefaultFallback(Action):
    def name(self):
        """return action name"""
        return "action_default_fallback"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]):
        """当机器无法保证正确判断时提供最高的intent让用户做选择
                如果是就继续流程，不是就转人工
        """
        # todo 转人工的可能性
        intent_name = tracker.get_intent_of_latest_message()
        if (intent_name == "action_default_fallback" or intent_name == "out_of_scope"):
            dispatcher.utter_message(response="utter_out_of_scope")
            return []
        message = "你是想问 '{}' ?".format(intent_name)
        buttons = [{'title': '是',
                    'payload': '/{}'.format(intent_name)},
                   {'title': '不是',
                    'payload': '/out_of_scope'}]
        dispatcher.utter_message(text=message, buttons=buttons)
        return []


class ActionAskOtherService(Action):
    """
    实现给出除上次业务外的其他业务选项
    """

    def name(self):
        """Unique identifier of the form; return action name"""

        return "action_ask_other_service"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]):

        """输出文本和可选的选项    return []"""

        buttons = []
        for t in SERVICE_TYPES:
            service_type = SERVICE_TYPES[t]
            ## payload as information if needed
            name = service_type.get("name")
            if (name == tracker.get_slot("last_service")):
                continue
            buttons.append({"title": "{}".format(name), 'payload': '/{}'.format(name)})
        dispatcher.utter_message(text="可以办理其他业务:")
        dispatcher.utter_message(buttons=buttons)
        return []


class ActionServiceInformation(Action):
    """
    给出所有能做的的业务选项
    """

    def name(self):
        """return action name"""
        return "action_service_information"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]):
        """输出文本和可选的选项   return[]"""
        buttons = []
        for t in SERVICE_TYPES:
            service_type = SERVICE_TYPES[t]
            name = service_type.get("name")
            buttons.append({"title": "{}".format(name), 'payload': '/{}'.format(name)})
        dispatcher.utter_message(text="我可以做到这些")
        dispatcher.utter_message(buttons=buttons)
        return []


# 需要traceback https://rasa.com/docs/rasa/reference/rasa/core/actions/forms/


"""
实现"查询基金" Jijin From
AskForJijinAction 询问Jijin entity if null
ValidateJijinForm 查看得到的Jijin entity 是否能识别
"""


# todo action_submit_Jijin_form 输出对应的Jjijin信息

class AskForJijinAction(Action):
    def name(self) -> Text:
        """return action name"""
        return "action_ask_Jijin"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """输出文本和其他业务选项  return []"""
        buttons = []
        buttons.append(
            # payload /intent{entity}
            {"title": "{}".format("办理其他业务"), 'payload': '/ask_other_service{"last_service":"基金查询","Jijin":"None"}'})
        dispatcher.utter_message(text="请问你要查询的基金名字或号码是多少？")
        dispatcher.utter_message(buttons=buttons)
        return []


# todo validation of form value
class ValidateJijinForm(FormValidationAction):
    def name(self) -> Text:
        """return action name"""
        return "validate_Jijin_form"

    @staticmethod
    def Jijin_db() -> List[Text]:
        """Database of supported 基金名称或者号码"""
        # todo 基金的list
        return []

    # todo
    def validate_Jijin(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if (slot_value == None): return {"Jijin": None}
        if slot_value.lower() in self.Jijin_db():

            return {"Jijin": slot_value}
        else:
            # validation failed, set this slot to None so that the
            # user will be asked for the slot again
            dispatcher.utter_message(text="基金‘{}'未查询到，请重新输入。".format(slot_value))
            return {"Jijin": None}


# 如果要加第一次遇到解释整个业务，加到rule或者story里防止一直重复 加新intent把这些放到后面

"""
实现"我要查基金" XuanJijin form
AskForRiskLevelAction 让用户选择风险评级
ValidateXuanJijinForm reset risk_level 判断risk_level是否符合category value
SubmitXuanJijinFormAction  当form完成后根据risk_level输出结果
"""


# todo SubmitXuanJijinFormAction根据接口得到不同风险评级需输出的基金信息

class AskForRiskLevelAction(Action):
    def name(self) -> Text:
        """return action name"""
        return "action_ask_risk_level"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """给出选项并根据选项给risk_level赋值"""
        buttons = []
        buttons.append({"title": "{}".format("低风险——安稳的享受收益"), 'payload': '/帮我选基金{"risk_level":"low"}'})
        buttons.append({"title": "{}".format("中风险——小波动来增大收益"), 'payload': '/帮我选基金{"risk_level":"medium"}'})
        buttons.append({"title": "{}".format("高风险——大波动来获取更大收益"), 'payload': '/帮我选基金{"risk_level":"high"}'})
        dispatcher.utter_message(text="请问你想选择哪种理财方式呢")
        dispatcher.utter_message(buttons=buttons)
        return []


class SubmitXuanJijinFormAction(Action):
    def name(self):
        """return action name"""
        return "action_submit_XuanJijin_form"

    # todo
    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]):
        """根据risk_level输出基金信息，并提供让客户继续流程的选项"""

        risk_level = tracker.get_slot('risk_level')
        if (risk_level == "low"):
            dispatcher.utter_message(text="这里提供的产品，期限较短，安全性高，回报稳健")
            # todo dispatcher.utter_meassge()输出想要的的基金
        elif (risk_level == "medium"):
            dispatcher.utter_message(text="这里提供的产品，期限为一年以上，波动相对较小")
            # todo dispatcher.utter_meassge()输出想要的的基金
        elif (risk_level == "high"):
            dispatcher.utter_message(text="这里提供的产品，富有潜力，收益不凡，但波动相对较大，适合有经验的投资者")
            # todo dispatcher.utter_meassge()输出想要的的基金
        buttons = []
        buttons.append({"title": "{}".format("看看其他理财方案"), 'payload': '/帮我选基金{"risk_level":"None"}'})
        buttons.append({"title": "{}".format("办理其他业务"),
                        'payload': '/ask_other_service{"last_service":"帮我选基金","risk_level":"None"}'})
        dispatcher.utter_message(buttons=buttons)
        # tracker.slots["risk_level"]=None
        # 如果通过return Slotset("risk_level", None) 完成，用户无法选择buttons，原因未知
        return []


class ValidateXuanJijinForm(FormValidationAction):
    def name(self) -> Text:
        """return action name"""
        return "validate_XuanJijin_form"

    def validate_risk_level(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """如果risk_level不符合category value reset
           导致story里每次会有两次的slot_was_set
        """
        if tracker.get_slot('risk_level') not in domain['slots']['risk_level']['values']:
            return {"risk_level": None}
        return {"risk_level": slot_value}
