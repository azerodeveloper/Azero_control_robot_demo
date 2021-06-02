import json



from azero_sdk_core.response_helper import get_text_content

from azero_sdk_model.interfaces.display import (

    RenderTemplateDirective,

    BodyTemplate1)



from azero_sdk_model.directive import *

from azero_sdk_model.dialog import *

from azero_sdk_core.skill_builder import SkillBuilder

from azero_sdk_core.dispatch_components import AbstractRequestHandler

import azero_sdk_core.utils as azero_utils

from azero_sdk_core.handler_input import HandlerInput

from azero_sdk_model import Response

from azero_sdk.skill_adapter import AzeroSkillAdapter

from azero_log.azero_logger import logger



import requests

import urllib3

import os

import base64

urllib3.disable_warnings()

"""

此处的ge78gifrc2f8x5需要换成用户自己在IOT网站的account_prefix

"""

thing_name_list=['TonyPi']

g_url = "https://kwk9n88tnxjzs2.iot.bj.soundai.cn:8443/things/${thingName}/shadow"

g_headers = {"Content-Type":"application/json"}

g_c_pwd = os.path.dirname(__file__)

"""

此处证书的6459b3fb78需要换成用户在IOT网站上申请的证书编号

"""

g_cert = ( g_c_pwd + "/pem/bc68232530-cert.pem", g_c_pwd + "/pem/bc68232530-private.key.pem")

def iot_post_request(body,thingName):

    return requests.post(g_url.replace('${thingName}',thingName), data=json.dumps(body), headers=g_headers, verify=g_c_pwd + "/pem/AzeroRootCA1.pem", cert=g_cert)


sb = SkillBuilder()



"""
Azero系统根据您自定义意图的意图标识自动生成此函数。
canhandle:判断传入此意图的请求是否要被此函数处理。默认判断规则为，请求中的意图标识与本意图标识匹配，且用户与技能一次对话交互已经完成即DialogState为COMPLETED。
handle:当canhandle返回为true时,自动执行。开发者需在handle内部编写此意图的业务逻辑代码。
用户与技能对话交互过程(DialogState)，有三种状态:STARTED、IN_PROGRESS、COMPLETED。
若意图不涉及多轮对话即可只关注COMPLETED状态。
若完成当前意图后希望转到新意图withShouldEndSession需设为false，且需返回Dialog的Directive。
"""
class CompletedDelegateHandler_stop(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("stop")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):
        # currentIntent = handler_input.request_envelope.request.intent
        speakOutput = '好的，不动了'
        body = {

            "state": {
                "desired": {
                    "powerState": "stop"
                }
            }
        }

        for thing_name in thing_name_list:
            resp = iot_post_request(body,thing_name)
            logger.info(thing_name + 'stop iot resp:' + str(resp), handler_input.request_envelope)

        return (
                handler_input.response_builder.add_directive(
                RenderTemplateDirective(
                    BodyTemplate1(
                        title=speakOutput,
                        text_content=get_text_content(primary_text=speakOutput))))
                .speak(speakOutput)
                .set_should_end_session(True)
                .response
        )

class CompletedDelegateHandler_AZERO_StopIntent(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("AZERO.StopIntent")(handler_input))
    def handle(self, handler_input):
        # currentIntent = handler_input.request_envelope.request.intent
        speakOutput = '好的，不动了'
        body = {

            "state": {
                "desired": {
                    "powerState": "stop"
                }
            }
        }

        for thing_name in thing_name_list:
            resp = iot_post_request(body,thing_name)
            logger.info(thing_name + 'AZERO.StopIntent iot resp:' + str(resp), handler_input.request_envelope)

        return (
                handler_input.response_builder.add_directive(
                RenderTemplateDirective(
                    BodyTemplate1(
                        title=speakOutput,
                        text_content=get_text_content(primary_text=speakOutput))))
                .speak(speakOutput)
                .set_should_end_session(True)
                .response
        )

"""
Azero系统根据您自定义意图的意图标识自动生成此函数。
canhandle:判断传入此意图的请求是否要被此函数处理。默认判断规则为，请求中的意图标识与本意图标识匹配，且用户与技能一次对话交互已经完成即DialogState为COMPLETED。
handle:当canhandle返回为true时,自动执行。开发者需在handle内部编写此意图的业务逻辑代码。
用户与技能对话交互过程(DialogState)，有三种状态:STARTED、IN_PROGRESS、COMPLETED。
若意图不涉及多轮对话即可只关注COMPLETED状态。
若完成当前意图后希望转到新意图withShouldEndSession需设为false，且需返回Dialog的Directive。
"""
class CompletedDelegateHandler_trun_right(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("trun_right")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):
        #currentIntent = handler_input.request_envelope.request.intent

        speakOutput = '好的，向右转'
        body = {

            "state": {
                "desired": {
                    "powerState": 'trun_right'
                }
            }
        }

        for thing_name in thing_name_list:
            resp = iot_post_request(body,thing_name)
            logger.info(thing_name + 'trun_right iot resp:' + str(resp), handler_input.request_envelope)

        return (
                handler_input.response_builder.add_directive(
                RenderTemplateDirective(
                    BodyTemplate1(
                        title=speakOutput,
                        text_content=get_text_content(primary_text=speakOutput))))
                .speak(speakOutput)
                .set_should_end_session(True)
                .response
        )
"""
Azero系统根据您自定义意图的意图标识自动生成此函数。
canhandle:判断传入此意图的请求是否要被此函数处理。默认判断规则为，请求中的意图标识与本意图标识匹配，且用户与技能一次对话交互已经完成即DialogState为COMPLETED。
handle:当canhandle返回为true时,自动执行。开发者需在handle内部编写此意图的业务逻辑代码。
用户与技能对话交互过程(DialogState)，有三种状态:STARTED、IN_PROGRESS、COMPLETED。
若意图不涉及多轮对话即可只关注COMPLETED状态。
若完成当前意图后希望转到新意图withShouldEndSession需设为false，且需返回Dialog的Directive。
"""
class CompletedDelegateHandler_trun_left(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("trun_left")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):
        # currentIntent = handler_input.request_envelope.request.intent
        speakOutput = '好的，向左转'
        body = {

            "state": {
                "desired": {
                    "powerState": 'trun_left'
                }
            }
        }

        for thing_name in thing_name_list:
            resp = iot_post_request(body,thing_name)
            logger.info(thing_name + 'trun_left iot resp:' + str(resp), handler_input.request_envelope)

        return (
                handler_input.response_builder.add_directive(
                RenderTemplateDirective(
                    BodyTemplate1(
                        title=speakOutput,
                        text_content=get_text_content(primary_text=speakOutput))))
                .speak(speakOutput)
                .set_should_end_session(True)
                .response
        )

"""
Azero系统根据您自定义意图的意图标识自动生成此函数。
canhandle:判断传入此意图的请求是否要被此函数处理。默认判断规则为，请求中的意图标识与本意图标识匹配，且用户与技能一次对话交互已经完成即DialogState为COMPLETED。
handle:当canhandle返回为true时,自动执行。开发者需在handle内部编写此意图的业务逻辑代码。
用户与技能对话交互过程(DialogState)，有三种状态:STARTED、IN_PROGRESS、COMPLETED。
若意图不涉及多轮对话即可只关注COMPLETED状态。
若完成当前意图后希望转到新意图withShouldEndSession需设为false，且需返回Dialog的Directive。
"""
class CompletedDelegateHandler_backward(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("backward")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):
        currentIntent = handler_input.request_envelope.request.intent
        step=""
        if currentIntent.slots['step'].value is not None:
            step=currentIntent.slots['step'].value
        else:
            step="1"

        speakOutput = '好的，往后退'+step+"步"
        body = {

            "state": {
                "desired": {
                    "powerState": 'backward',
                    "step": step    # step为字符串
                }
            }
        }

        for thing_name in thing_name_list:
            resp = iot_post_request(body,thing_name)
            logger.info(thing_name + 'backward iot resp:' + str(resp), handler_input.request_envelope)

        return (
                handler_input.response_builder.add_directive(
                RenderTemplateDirective(
                    BodyTemplate1(
                        title=speakOutput,
                        text_content=get_text_content(primary_text=speakOutput))))
                .speak(speakOutput)
                .set_should_end_session(True)
                .response
        )

class CompletedDelegateHandler_AZERO_PlayProgressIntent(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("AZERO.PlayProgressIntent")(handler_input))
    def handle(self, handler_input):
        currentIntent = handler_input.request_envelope.request.intent
        step = "1"
        body = {}
        speakOutput = ''
        if currentIntent.slots['action'].value is not None:
            direction=currentIntent.slots['action'].value
            if direction == 'FAST_FORWARD':
                speakOutput = '好的，往前走'
                body = {
                    "state": {
                        "desired": {
                        "powerState": 'forward',
                        "step": step    # step为字符串
                        }
                    }
                }
            elif direction == 'REWIND':
                speakOutput = '好的，往后退'
                body = {
                    "state": {
                        "desired": {
                        "powerState": 'backward',
                        "step": step    # step为字符串
                        }
                    }
                }

        for thing_name in thing_name_list:
            resp = iot_post_request(body,thing_name)
            logger.info(thing_name + 'PlayProgressIntent iot resp:' + str(resp), handler_input.request_envelope)

        return (
                handler_input.response_builder
                .speak(speakOutput)
                .set_should_end_session(True)
                .response
        )




"""
Azero系统根据您自定义意图的意图标识自动生成此函数。
canhandle:判断传入此意图的请求是否要被此函数处理。默认判断规则为，请求中的意图标识与本意图标识匹配，且用户与技能一次对话交互已经完成即DialogState为COMPLETED。
handle:当canhandle返回为true时,自动执行。开发者需在handle内部编写此意图的业务逻辑代码。
用户与技能对话交互过程(DialogState)，有三种状态:STARTED、IN_PROGRESS、COMPLETED。
若意图不涉及多轮对话即可只关注COMPLETED状态。
若完成当前意图后希望转到新意图withShouldEndSession需设为false，且需返回Dialog的Directive。
"""
class CompletedDelegateHandler_forward(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("forward")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):
        step=""
        currentIntent = handler_input.request_envelope.request.intent
        if currentIntent.slots['step'].value is not None:
            step=currentIntent.slots['step'].value
        else:
            step="1"

        speakOutput = '好的，往前走'+step+"步"
        body = {

            "state": {
                "desired": {
                    "powerState": 'forward',
                    "step": step   # step为字符串
                }
            }
        }

        for thing_name in thing_name_list:
            resp = iot_post_request(body,thing_name)
            logger.info(thing_name + 'forward iot resp:' + str(resp), handler_input.request_envelope)

        return (
                handler_input.response_builder.add_directive(
                RenderTemplateDirective(
                    BodyTemplate1(
                        title=speakOutput,
                        text_content=get_text_content(primary_text=speakOutput))))
                .speak(speakOutput)
                .set_should_end_session(True)
                .response
        )


"""
Azero系统根据您自定义意图的意图标识自动生成此函数。
canhandle:判断传入此意图的请求是否要被此函数处理。默认判断规则为，请求中的意图标识与本意图标识匹配，且用户与技能一次对话交互已经完成即DialogState为COMPLETED。
handle:当canhandle返回为true时,自动执行。开发者需在handle内部编写此意图的业务逻辑代码。
用户与技能对话交互过程(DialogState)，有三种状态:STARTED、IN_PROGRESS、COMPLETED。
若意图不涉及多轮对话即可只关注COMPLETED状态。
若完成当前意图后希望转到新意图withShouldEndSession需设为false，且需返回Dialog的Directive。
"""
class CompletedDelegateHandler_exercise(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("exercise")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):
        # currentIntent = handler_input.request_envelope.request.intent
        speakOutput = '好的，健身开始'
        body = {

            "state": {
                "desired": {
                    "powerState": 'exercise'
                }
            }
        }

        for thing_name in thing_name_list:
            resp = iot_post_request(body,thing_name)
            logger.info(thing_name + 'exercise iot resp:' + str(resp), handler_input.request_envelope)

        return (
                handler_input.response_builder.add_directive(
                RenderTemplateDirective(
                    BodyTemplate1(
                        title=speakOutput,
                        text_content=get_text_content(primary_text=speakOutput))))
                .speak(speakOutput)
                .set_should_end_session(True)
                .response
        )


"""
Azero系统根据您自定义意图的意图标识自动生成此函数。
canhandle:判断传入此意图的请求是否要被此函数处理。默认判断规则为，请求中的意图标识与本意图标识匹配，且用户与技能一次对话交互已经完成即DialogState为COMPLETED。
handle:当canhandle返回为true时,自动执行。开发者需在handle内部编写此意图的业务逻辑代码。
用户与技能对话交互过程(DialogState)，有三种状态:STARTED、IN_PROGRESS、COMPLETED。
若意图不涉及多轮对话即可只关注COMPLETED状态。
若完成当前意图后希望转到新意图withShouldEndSession需设为false，且需返回Dialog的Directive。
"""
class CompletedDelegateHandler_wushu(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("wushu")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):
        # currentIntent = handler_input.request_envelope.request.intent
        speakOutput = '武术表演开始'
        body = {

            "state": {
                "desired": {
                    "powerState": 'wushu'
                }
            }
        }

        for thing_name in thing_name_list:
            resp = iot_post_request(body,thing_name)
            logger.info(thing_name + 'wushu iot resp:' + str(resp), handler_input.request_envelope)

        return (
                handler_input.response_builder.add_directive(
                RenderTemplateDirective(
                    BodyTemplate1(
                        title=speakOutput,
                        text_content=get_text_content(primary_text=speakOutput))))
                .speak(speakOutput)
                .set_should_end_session(True)
                .response
        )



"""
Azero系统根据您自定义意图的意图标识自动生成此函数。
canhandle:判断传入此意图的请求是否要被此函数处理。默认判断规则为，请求中的意图标识与本意图标识匹配，且用户与技能一次对话交互已经完成即DialogState为COMPLETED。
handle:当canhandle返回为true时,自动执行。开发者需在handle内部编写此意图的业务逻辑代码。
用户与技能对话交互过程(DialogState)，有三种状态:STARTED、IN_PROGRESS、COMPLETED。
若意图不涉及多轮对话即可只关注COMPLETED状态。
若完成当前意图后希望转到新意图withShouldEndSession需设为false，且需返回Dialog的Directive。
"""
class CompletedDelegateHandler_dance(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("dance")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):
        # currentIntent = handler_input.request_envelope.request.intent
        speakOutput = '好的，让我给您跳个舞'
        body = {

            "state": {
                "desired": {
                    "powerState": 'dance'
                }
            }
        }

        for thing_name in thing_name_list:
            resp = iot_post_request(body,thing_name)
            logger.info(thing_name + 'dance iot resp:' + str(resp), handler_input.request_envelope)

        return (
                handler_input.response_builder.add_directive(
                RenderTemplateDirective(
                    BodyTemplate1(
                        title=speakOutput,
                        text_content=get_text_content(primary_text=speakOutput))))
                .speak(speakOutput)
                .set_should_end_session(True)
                .response
        )



"""

Azero系统根据您自定义意图的意图标识自动生成此函数。

canhandle:判断传入此意图的请求是否要被此函数处理。默认判断规则为，请求中的意图标识与本意图标识匹配，且用户与技能一次对话交互已经完成即DialogState为COMPLETED。

handle:当canhandle返回为true时,自动执行。开发者需在handle内部编写此意图的业务逻辑代码。

用户与技能对话交互过程(DialogState)，有三种状态:STARTED、IN_PROGRESS、COMPLETED。

若意图不涉及多轮对话即可只关注COMPLETED状态。

若完成当前意图后希望转到新意图withShouldEndSession需设为false，且需返回Dialog的Directive。

"""

class CompletedDelegateHandler_seeyou(AbstractRequestHandler):

    def can_handle(self, handler_input):

        return (azero_utils.is_request_type("IntentRequest")(handler_input) and

               azero_utils.is_intent_name("seeyou")(handler_input) and

               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')

    def handle(self, handler_input):

        speak_output = ''

        body = {

            "state": {

                "desired": {

                    "powerState": 'seeyou'

                }

            }

        }





        for thing_name in thing_name_list:

            resp = iot_post_request(body,thing_name)

            logger.info(thing_name + 'seeyou iot resp:' + str(resp.json()), handler_input.request_envelope)

        # with open('/pem/AzeroRootCA1.pem', 'a',encoding="utf-8") as wf:
        #         line = f.readline()



        speak_output = '各位领导再见'



        return (

            handler_input.response_builder.add_directive(

                RenderTemplateDirective(

                    BodyTemplate1(

                        title=speak_output,

                        text_content=get_text_content(primary_text=speak_output))))

                .speak(speak_output)

                .set_should_end_session(True)

                .response

        )



"""

Azero系统根据您自定义意图的意图标识自动生成此函数。

canhandle:判断传入此意图的请求是否要被此函数处理。默认判断规则为，请求中的意图标识与本意图标识匹配，且用户与技能一次对话交互已经完成即DialogState为COMPLETED。

handle:当canhandle返回为true时,自动执行。开发者需在handle内部编写此意图的业务逻辑代码。

用户与技能对话交互过程(DialogState)，有三种状态:STARTED、IN_PROGRESS、COMPLETED。

若意图不涉及多轮对话即可只关注COMPLETED状态。

若完成当前意图后希望转到新意图withShouldEndSession需设为false，且需返回Dialog的Directive。

"""

class CompletedDelegateHandler_welcome(AbstractRequestHandler):

    def can_handle(self, handler_input):

        return (azero_utils.is_request_type("IntentRequest")(handler_input) and

               azero_utils.is_intent_name("welcome")(handler_input) and

               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')

    def handle(self, handler_input):

        speak_output = ''

        body = {

            "state": {

                "desired": {

                    "powerState": 'welcome'

                }

            }

        }



        for thing_name in thing_name_list:

            resp = iot_post_request(body,thing_name)

            logger.info(thing_name + 'welcome iot resp:' + str(resp), handler_input.request_envelope)



        speak_output = '欢迎各位领导'



        return (

            handler_input.response_builder.add_directive(

                RenderTemplateDirective(

                    BodyTemplate1(

                        title=speak_output,

                        text_content=get_text_content(primary_text=speak_output))))

                .speak(speak_output)

                .set_should_end_session(True)

                .response

        )





"""

用户取消和退出或者错误退出时的Handle

"""

class SessionEndedRequestHandler(AbstractRequestHandler):

    """Handler for Session End."""



    def can_handle(self, handler_input):

        # type: (HandlerInput) -> bool

        return azero_utils.is_request_type("SessionEndedRequest")(handler_input)



    def handle(self, handler_input):

        # type: (HandlerInput) -> Response



        # Any cleanup logic goes here.



        return handler_input.response_builder.speak('已退出当前意图').set_should_end_session(True).response



class IntentRequestHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):

        # type: (HandlerInput) -> bool

        return azero_utils.is_request_type("IntentRequest")(handler_input)



    def handle(self, handler_input):

        speak_output='欢迎使用技能'

        return (

            handler_input.response_builder.add_directive(

                RenderTemplateDirective(

                    BodyTemplate1(

                        title=speak_output,

                        text_content=get_text_content(primary_text=speak_output))))

                .speak(speak_output)

                .set_should_end_session(True)

                .response

        )

"""

所有意图函数都需要添加到add_request_handler中。保证Azero系统能正常将用户的意图请求传入*对应的意图函数中进行处理。服务部署一般会自动生成添加代码。

"""









def invoke_skill(app):
    sb.add_request_handler(CompletedDelegateHandler_AZERO_StopIntent())
    sb.add_request_handler(CompletedDelegateHandler_AZERO_PlayProgressIntent())
    sb.add_request_handler(CompletedDelegateHandler_trun_right())
    sb.add_request_handler(CompletedDelegateHandler_trun_left())
    sb.add_request_handler(CompletedDelegateHandler_backward())
    sb.add_request_handler(CompletedDelegateHandler_stop())
    sb.add_request_handler(CompletedDelegateHandler_forward())
    sb.add_request_handler(CompletedDelegateHandler_exercise())
    sb.add_request_handler(CompletedDelegateHandler_wushu())
    sb.add_request_handler(CompletedDelegateHandler_dance())

    sb.add_request_handler(CompletedDelegateHandler_seeyou())

    sb.add_request_handler(CompletedDelegateHandler_welcome())



    sb.add_request_handler(SessionEndedRequestHandler())

    sb.add_request_handler(IntentRequestHandler())

    skill_adapter = AzeroSkillAdapter(skill=sb.create(), skill_id='606fd4970179b500068b483f', app = app)

    result = skill_adapter.dispatch_request()

    return result

