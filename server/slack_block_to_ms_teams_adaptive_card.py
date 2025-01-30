import json
import re
from html import escape
import uuid
import emoji


def slack_to_teams_emoji(slack_text):
    def replace_emoji(match):
        short_name = match.group(0)
        print(short_name)
        return emoji.emojize(short_name,language='alias')

    return re.sub(r':\w+:', replace_emoji, slack_text)

# This is a very basic conversion, it will not work for all cases 
def markdown_to_rich_text(markdown_text):
    rich_text = markdown_text.replace('*', '**') \
                              .replace('~', '~~')
    rich_text = re.sub(r'<(.*?)\|(.*?)>', r'[\2](\1)', rich_text)
    rich_text = rich_text.replace('\n', '\n\n')
    rich_text = slack_to_teams_emoji(rich_text) 
    return rich_text


def process_text(text_block, is_context_block=False):
    text = text_block["text"]

    if text_block["type"] == "plain_text":
        text = slack_to_teams_emoji(text)
    elif text_block["type"] == "mrkdwn":
        text = markdown_to_rich_text(text)

    return {
        "type": "TextBlock",
        "text": text,
        "wrap": True,
        "isSubtle": is_context_block
    }

def process_fields(fields):
    fact_set = {
        "type": "FactSet",
        "facts": []
    }
    for field in fields:
        field_text = process_text(field, False)["text"].replace("\n", "").replace("*", "")
        if ":" in field_text:
            fact_parts = field_text.split(":")
            fact_set["facts"].append({
                "title": fact_parts[0].strip(),
                "value": fact_parts[1].strip()
            })
        else:
            fact_set["facts"].append({
                "title": "_Insert_Key_Here_",
                "value": field_text
            })
    return fact_set

def process_users_select(element):
    return {
        "type": "Input.ChoiceSet",
        "id": element.get("action_id", str(uuid.uuid4())),
        "placeholder": element["placeholder"]["text"],
        "choices": []  # You will need to populate this with users
    }

def process_conversations_select(element):
    return {
        "type": "Input.ChoiceSet",
        "id": element.get("action_id", str(uuid.uuid4())),
        "placeholder": element["placeholder"]["text"],
        "choices": []  # You will need to populate this with conversations
    }


def process_multi_conversations_select(element):
    return {
        "type": "Input.ChoiceSet",
        "id": element.get("action_id", str(uuid.uuid4())),
        "placeholder": element["placeholder"]["text"],
        "choices": [],  # You will need to populate this with conversations
        "isMultiSelect": True
    }


def process_static_select(element):
    choices = [
        {
            "title": option["text"]["text"],
            "value": option.get("value", "insert_some_value_here" )
        }
        for option in element["options"]
    ]

    return {
        "type": "Input.ChoiceSet",
        "id": element.get("action_id", str(uuid.uuid4())),
        "placeholder": element["placeholder"]["text"],
        "choices": choices
    }


def process_button(element):
    return {
        "type": "ActionSet",
        "actions": [
            {
                "type": "Action.Submit",
                "title": element["text"]["text"],
                "data": {
                    "action_id": element.get("action_id", str(uuid.uuid4())),
                    "value": element.get("value", "insert_some_value_here" )
                }
            }
        ]
    }


def process_image(element):
    return {
        "type": "Image",
        "url": element["image_url"],
        "altText": element["alt_text"]
    }


def process_datepicker(element):
    return {
        "type": "Input.Date",
        "id": element.get("action_id", str(uuid.uuid4())),
        "placeholder": element["placeholder"]["text"],
        "value": element["initial_date"]
    }


def process_checkboxes(element):
    choices = [
        {
            "title": option["text"]["text"],
            "value": option.get("value", "insert_some_value_here" )
        }
        for option in element["options"]
    ]

    return {
        "type": "Input.ChoiceSet",
        "id": element.get("action_id", str(uuid.uuid4())),
        "choices": choices,
        "isMultiSelect": True
    }


def process_radio_buttons(element):
    choices = [
        {
            "title": option["text"]["text"],
            "value": option.get("value", "insert_some_value_here" )
        }
        for option in element["options"]
    ]

    return {
        "type": "Input.ChoiceSet",
        "id": element.get("action_id", str(uuid.uuid4())),
        "choices": choices,
        "isMultiSelect": False
    }


def process_timepicker(element):
    return {
        "type": "Input.Time",
        "id": element.get("action_id", str(uuid.uuid4())),
        "placeholder": element["placeholder"]["text"],
        "value": element["initial_time"]
    }

def process_element(element):
    element_type = element["type"]
    processing_functions = {
        "users_select": process_users_select,
        "static_select": process_static_select,
        "button": process_button,
        "image": process_image,
        "datepicker": process_datepicker,
        "checkboxes": process_checkboxes,
        "radio_buttons": process_radio_buttons,
        "timepicker": process_timepicker,
        "conversations_select": process_conversations_select,
        "multi_conversations_select": process_multi_conversations_select
    }

    return processing_functions[element_type](element)

def process_accessory(accessory):
    return process_element(accessory)

def process_image_block(block):
    return process_image(block)

#processing blocks of type section
def process_section_block(block):
    section = []

    if "text" in block:
        section.append(process_text(block["text"]))

    if "fields" in block:
        section.append(process_fields(block["fields"]))
    
    if "accessory" in block:
        accessory_item = process_accessory(block["accessory"])
        if accessory_item:
            column_set = {
                "type": "ColumnSet",
                "columns": [
                    {
                        "type": "Column",
                        "width": "stretch",
                        "verticalContentAlignment": "center",
                        "items": section
                    },
                    {
                        "type": "Column",
                        "width": "auto",
                        "verticalContentAlignment": "center",
                        "items": [accessory_item]
                    }
                ]
            }
            return [column_set]

    return section

# Function to process elements in blocks of type actions and context
def process_elements(elements, is_context_block=False):
    teams_elements = {
        "type": "ColumnSet",
        "columns": []
    }

    for element in elements:
        if element["type"] == "mrkdwn" or element["type"] == "plain_text":
            teams_element = process_text(element, is_context_block)
        else:
            teams_element = process_element(element)

        column = {
            "type": "Column",
            "width": "auto",
            "verticalContentAlignment": "center",
            "items": [teams_element]
        }

        teams_elements["columns"].append(column)

    return [teams_elements]

def process_header_block(block):
    text_block = process_text(block["text"], False)
    text_block["size"] = "ExtraLarge"
    text_block["weight"] = "Bolder"
    return text_block

def process_context_block(block):
    return process_elements(block["elements"], is_context_block=True)

def process_divider_block(block):
    return {
        "type": "Separator"
    }


def convert_slack_block_to_adaptive_card(slack_json):
    slack_data = json.loads(slack_json)
    ms_teams_adaptive_card = {
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": []
    }
    
    last_block_was_divider = False
    
    for block in slack_data["blocks"]:
        if block["type"] == "section":
            section_block = process_section_block(block)
            if last_block_was_divider:
                section_block[0]["separator"] = True
                last_block_was_divider = False
            ms_teams_adaptive_card["body"].extend(section_block)
        elif block["type"] == "actions":
            teams_elements = process_elements(block["elements"])
            if last_block_was_divider:
                teams_elements[0]["separator"] = True
                last_block_was_divider = False
            ms_teams_adaptive_card["body"].extend(teams_elements)
        elif block["type"] == "header":
            header_block = process_header_block(block)
            if last_block_was_divider:
                header_block["separator"] = True
                last_block_was_divider = False
            ms_teams_adaptive_card["body"].append(header_block)
        elif block["type"] == "context":
            teams_elements = process_context_block(block)
            if last_block_was_divider:
                teams_elements[0]["separator"] = True
                last_block_was_divider = False
            ms_teams_adaptive_card["body"].extend(teams_elements)
        elif block["type"] == "divider":
            last_block_was_divider = True
        elif block["type"] == "image":
            image_block = process_image_block(block)
            if last_block_was_divider:
                image_block["separator"] = True
                last_block_was_divider = False
            ms_teams_adaptive_card["body"].append(image_block)
        
        # Add more supported block types here, such as "divider", "image", etc.

    return ms_teams_adaptive_card