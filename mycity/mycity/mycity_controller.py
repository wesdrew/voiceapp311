"""
Controller for mycity voice app.

This class handles all voice requests.
"""

from __future__ import print_function
from mycity.mycity_request_data_model import MyCityRequestDataModel
from mycity.mycity_response_data_model import MyCityResponseDataModel
from .intents.user_address_intent import set_address_in_session, \
    get_address_from_session, request_user_address_response
from .intents.trash_intent import get_trash_day_info
from .intents.unhandled_intent import unhandled_intent
from .intents.get_alerts_intent import get_alerts_intent
from .intents.snow_parking_intent import get_snow_emergency_parking_intent
from .intents import intent_constants


LOG_CLASS = '\n\n[class: MyCityController]'


# dictionaries mapping intent names to functions with logic to process
# that intent. Intents that need an address for the user before execution are
# in a separate dictionary. The controller will check for an address and may 
# request the user's address before executing the intent. "SetAddressIntent"
# is a special case and is handled separately. Functions defined in this 
# module are added to these dictionaries after their definition

INTENTS_NO_ADDRESS_NEEDED = { "GetAddressIntent" : get_address_from_session,
                              "GetAlertsIntent" : get_alerts_intent,
                              "UnhandledIntent" : unhandled_intent }


INTENTS_NEED_ADDRESS = { "TrashDayIntent" : get_trash_day_info,
                         "SnowParkingIntent" : get_snow_emergency_parking_intent }


def execute_request(mycity_request):
    """
    Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print(
        LOG_CLASS,
        '[method: main]',
        'MyCityRequestDataModel received:\n',
        str(mycity_request)
    )

    # TODO: This section should be generalized for all platforms if possible
    """
    Uncomment this if statement and populate with your skill's application ID 
    to prevent someone else from configuring a skill that sends requests to 
    this function.
    """
    # if (mcd.application_id !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if mycity_request.is_new_session:
        on_session_started(mycity_request)

    if mycity_request.request_type == "LaunchRequest":
        return on_launch(mycity_request)
    elif mycity_request.request_type == "IntentRequest":
        return on_intent(mycity_request)
    elif mycity_request.request_type == "SessionEndedRequest":
        return on_session_ended(mycity_request)


def on_session_started(mycity_request):
    """
    Called when the session starts.
    """
    print(
        LOG_CLASS,
        '[method: on_session_started]',
        '[requestId: ' + str(mycity_request.request_id) + ']',
        '[sessionId: ' + str(mycity_request.session_id) + ']',
        (
            '[request object: ' + str(mycity_request) + ']' if
            isinstance(mycity_request, MyCityRequestDataModel) else
            '[request object: ' +
            'ERROR - request should be a MyCityRequestDataModel.]'
        )
    )

def on_launch(mycity_request):
    """
    Called when the user launches the skill without specifying what
    they want.
    """
    print(
        LOG_CLASS,
        '[method: on_launch]',
        '[requestId: ' + str(mycity_request.request_id) + ']',
        '[sessionId: ' + str(mycity_request.session_id) + ']'
    )

    # Dispatch to your skill's launch
    return get_welcome_response(mycity_request)


def on_intent(mycity_request):
    """
    If the event type is "request" and the request type is "IntentRequest",
    this function is called to execute the logic associated with the
    provided intent and build a response.
    """

    print(
        LOG_CLASS,
        '[method: on_intent]',
        '[intent: ' + mycity_request.intent_name + ']',
        'MyCityRequestDataModel received:',
        mycity_request
    )
    addr_key = intent_constants.CURRENT_ADDRESS_KEY
    intent_prompted_from = intent_constants.ADDRESS_PROMPTED_FROM_INTENT

    # Check if the user is setting the address. This is special cased
    # since they may have been prompted for this info from another intent
    if mycity_request.intent_name == "SetAddressIntent":
        set_address_in_session(mycity_request)
        if intent_prompted_from in mycity_request.session_attributes:
            # User was prompted for address from another intent.
            # Set our current intent to be that original intent now that
            # we have set the address.
            mycity_request.intent_name = \
                mycity_request.session_attributes[intent_prompted_from]
            print("Address set after calling another intent. Redirecting "
                  "intent to {}".format(mycity_request.intent_name))
            # Delete the session key indicating this intent was called
            # from another intent.
            del mycity_request.session_attributes[intent_prompted_from]
        else:
            return get_address_from_session(mycity_request) 

    # session_attributes = session.get("attributes", {})
    if mycity_request.intent_name in INTENTS_NO_ADDRESS_NEEDED:
        return INTENTS_NO_ADDRESS_NEEDED[mycity_request.intent_name](mycity_request)
    elif mycity_request.intent_name in INTENTS_NEED_ADDRESS:
        return request_user_address_response(mycity_request) \
            if addr_key not in mycity_request.session_attributes \
            else INTENTS_NEED_ADDRESS[mycity_request.intent_name](mycity_request)
    else:
        raise ValueError("Invalid Intent")


def on_session_ended(mycity_request):
    """
    Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print(
        LOG_CLASS,
        '[method: on_session_ended]',
        'MyCityRequestDataModel received:',
        str(mycity_request)
    )
    return MyCityResponseDataModel()
    # add cleanup logic here


def get_welcome_response(mycity_request):
    """
    If we wanted to initialize the session to have some attributes we could
    add those here.
    """
    print(
        LOG_CLASS,
        '[method: get_welcome_response]'
    )
    mycity_response = MyCityResponseDataModel()
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = "Welcome"
    mycity_response.output_speech = \
        "Welcome to the Boston Public Services skill. How can I help you? "

    # If the user either does not reply to the welcome message or says
    # something that is not understood, they will be prompted again with
    # this text.
    mycity_response.reprompt_text = \
        "For example, you can tell me your address by saying, " \
        "\"my address is\" followed by your address."
    mycity_response.should_end_session = False
    return mycity_response

# add function to intents dict
INTENTS_NO_ADDRESS_NEEDED["AMAZON.HelpIntent"] = get_welcome_response


def handle_session_end_request(mycity_request):
    mycity_response = MyCityResponseDataModel()
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = "Boston Public Services - Thanks"
    mycity_response.output_speech = \
        "Thank you for using the Boston Public Services skill. " \
        "See you next time!"
    mycity_response.should_end_session = True
    return mycity_response

# add function to intents dict
INTENTS_NO_ADDRESS_NEEDED["AMAZON.StopIntent"] = handle_session_end_request
INTENTS_NO_ADDRESS_NEEDED["AMAZON.CancelIntent"] = handle_session_end_request

