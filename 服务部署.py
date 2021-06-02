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

此处的xe1xrpavoal2vo需要换成用户自己在IOT网站的account_prefix

"""

thing_name_list=['spiderman']

g_url = "https://xe1xrpavoal2vo.iot.bj.soundai.cn:8443/things/${thingName}/shadow"

g_headers = {"Content-Type":"application/json"}

g_c_pwd = os.path.dirname(__file__)

"""

此处证书的5c2b5f60bc需要换成用户在IOT网站上申请的证书编号

"""

g_cert = ( g_c_pwd + "/pem/5c2b5f60bc-cert.pem", g_c_pwd + "/pem/5c2b5f60bc-private.key.pem")



sb = SkillBuilder()

def iot_post_request(body,thingName):
    return requests.post(g_url.replace('${thingName}',thingName), data=json.dumps(body), headers=g_headers, verify=g_c_pwd + "/pem/AzeroRootCA1.pem", cert=g_cert)

"""
Azero系统根据您自定义意图的意图标识自动生成此函数。
canhandle:判断传入此意图的请求是否要被此函数处理。默认判断规则为，请求中的意图标识与本意图标识匹配，且用户与技能一次对话交互已经完成即DialogState为COMPLETED。
handle:当canhandle返回为true时,自动执行。开发者需在handle内部编写此意图的业务逻辑代码。
用户与技能对话交互过程(DialogState)，有三种状态:STARTED、IN_PROGRESS、COMPLETED。
若意图不涉及多轮对话即可只关注COMPLETED状态。
若完成当前意图后希望转到新意图withShouldEndSession需设为false，且需返回Dialog的Directive。
"""
class CompletedDelegateHandler_dancing(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("dancing")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):

        speak_output = ''

        body = {

            "state": {

                "desired": {

                    "powerState": 'dance'

                }

            }

        }

        

        

        for thing_name in thing_name_list:  

            resp = iot_post_request(body,thing_name)

            logger.info(thing_name + 'dance iot resp:' + str(resp.json()), handler_input.request_envelope)

        

        speak_output = '好的，我来给你跳支舞'



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
class CompletedDelegateHandler_backward(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("backward")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):
        currentIntent = handler_input.request_envelope.request.intent
        steps=""
        if currentIntent.slots['steps'].value is not None:
            steps=currentIntent.slots['steps'].value
        else:
            steps="1"

        speakOutput = '好的，往后退'+steps+"步"
        body = {

            "state": {
                "desired": {
                    "powerState": 'backward',
                    "steps": steps    
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
        currentIntent = handler_input.request_envelope.request.intent
        steps=""
        if currentIntent.slots['steps'].value is not None:
            steps=currentIntent.slots['steps'].value
        else:
            steps="1"

        speakOutput = '好的，往前走'+steps+"步"
        body = {

            "state": {
                "desired": {
                    "powerState": 'forward',
                    "steps": steps    # steps为字符串
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


class CompletedDelegateHandler_AZERO_PlayProgressIntent(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("AZERO.PlayProgressIntent")(handler_input))
    def handle(self, handler_input):
        currentIntent = handler_input.request_envelope.request.intent
        steps = "1"
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
                        "steps": steps    # step为字符串
                        }
                    }
                }
            elif direction == 'REWIND':
                speakOutput = '好的，往后退'
                body = {
                    "state": {
                        "desired": {
                        "powerState": 'backward',
                        "steps": steps    # step为字符串
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
class CompletedDelegateHandler_turn_right(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("turn_right")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):

        speak_output = ''

        body = {

            "state": {

                "desired": {

                    "powerState": 'trun_right'

                }

            }

        }

        

        

        for thing_name in thing_name_list:  

            resp = iot_post_request(body,thing_name)

            logger.info(thing_name + 'trun_right iot resp:' + str(resp.json()), handler_input.request_envelope)

        

        speak_output = '右转完成'



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
class CompletedDelegateHandler_turn_left(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("turn_left")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):

        speak_output = ''

        body = {

            "state": {

                "desired": {

                    "powerState": 'trun_left'

                }

            }

        }

        

        

        for thing_name in thing_name_list:  

            resp = iot_post_request(body,thing_name)

            logger.info(thing_name + 'trun_left iot resp:' + str(resp.json()), handler_input.request_envelope)

        

        speak_output = '左转完成'



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
class CompletedDelegateHandler_threat(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("threat")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):

        speak_output = ''

        body = {

            "state": {

                "desired": {

                    "powerState": 'threat'

                }

            }

        }

        

        

        for thing_name in thing_name_list:  

            resp = iot_post_request(body,thing_name)

            logger.info(thing_name + 'threat iot resp:' + str(resp.json()), handler_input.request_envelope)

        

        speak_output = '吼'



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
class CompletedDelegateHandler_pushup(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("pushup")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):

        speak_output = ''

        body = {

            "state": {

                "desired": {

                    "powerState": 'exercise'

                }

            }

        }

        

        

        for thing_name in thing_name_list:  

            resp = iot_post_request(body,thing_name)

            logger.info(thing_name + 'exercise iot resp:' + str(resp.json()), handler_input.request_envelope)

        

        speak_output = '好的，健身开始了！'



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
class CompletedDelegateHandler_steping(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("steping")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):

        speak_output = ''

        body = {

            "state": {

                "desired": {

                    "powerState": 'steping'

                }

            }

        }

        

        

        for thing_name in thing_name_list:  

            resp = iot_post_request(body,thing_name)

            logger.info(thing_name + 'steping iot resp:' + str(resp.json()), handler_input.request_envelope)

        

        speak_output = '好的，我来跺跺脚'



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
class CompletedDelegateHandler_wave_body(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("wave_body")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):

        speak_output = ''

        body = {

            "state": {

                "desired": {

                    "powerState": 'wave_body'

                }

            }

        }

        

        

        for thing_name in thing_name_list:  

            resp = iot_post_request(body,thing_name)

            logger.info(thing_name + 'wave_body iot resp:' + str(resp.json()), handler_input.request_envelope)

        

        speak_output = '扭来扭去'



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
class CompletedDelegateHandler_attack_forward(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (azero_utils.is_request_type("IntentRequest")(handler_input) and
               azero_utils.is_intent_name("attack_forward")(handler_input) and
               azero_utils.get_dialog_state(handler_input).value == 'COMPLETED')
    def handle(self, handler_input):

        speak_output = ''

        body = {

            "state": {

                "desired": {

                    "powerState": 'attack_forward'

                }

            }

        }

        

        

        for thing_name in thing_name_list:  

            resp = iot_post_request(body,thing_name)

            logger.info(thing_name + 'attack_forward iot resp:' + str(resp.json()), handler_input.request_envelope)

        

        speak_output = '向前进攻'



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

        

        speak_output = '各位再见'



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



        speak_output = '欢迎各位'



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
    sb.add_request_handler(CompletedDelegateHandler_dancing())
    sb.add_request_handler(CompletedDelegateHandler_backward())
    sb.add_request_handler(CompletedDelegateHandler_forward())
    sb.add_request_handler(CompletedDelegateHandler_AZERO_PlayProgressIntent())
    sb.add_request_handler(CompletedDelegateHandler_turn_right())
    sb.add_request_handler(CompletedDelegateHandler_turn_left())
    sb.add_request_handler(CompletedDelegateHandler_threat())
    sb.add_request_handler(CompletedDelegateHandler_pushup())
    sb.add_request_handler(CompletedDelegateHandler_steping())
    sb.add_request_handler(CompletedDelegateHandler_wave_body())
    sb.add_request_handler(CompletedDelegateHandler_attack_forward())

    sb.add_request_handler(CompletedDelegateHandler_seeyou())

    sb.add_request_handler(CompletedDelegateHandler_welcome())



    sb.add_request_handler(SessionEndedRequestHandler())

    sb.add_request_handler(IntentRequestHandler())

    skill_adapter = AzeroSkillAdapter(skill=sb.create(), skill_id='60a1d373b0b8f00006d91104', app = app)

    result = skill_adapter.dispatch_request()

    return result


