from app.models import BeveragePublic
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage

GET_RECIPES_JSON_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "recipe_list",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "cocktails": {
                    "type": "array",
                    "description": "A list of cocktails objects with detailed information.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The name of the cocktail/drink.",
                            },
                            "ingredients": {
                                "type": "array",
                                "description": "List of ingredients required for the recipe.",
                                "items": {
                                    "type": "string",
                                    "description": "The description of the ingredient.",
                                },
                            },
                            "steps": {
                                "type": "array",
                                "description": "Ordered steps to prepare the cocktail.",
                                "items": {
                                    "type": "string",
                                    "description": "Description of a preparation step.",
                                },
                            },
                        },
                        "required": ["title", "ingredients", "steps"],
                        "additionalProperties": False,
                    },
                },
                "sideDishes": {
                    "type": "array",
                    "description": "A list of side dishes objects with detailed information.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The name of the meal.",
                            },
                            "ingredients": {
                                "type": "array",
                                "description": "List of ingredients required for the dish.",
                                "items": {
                                    "type": "string",
                                    "description": "The description of the ingredient.",
                                },
                            },
                            "steps": {
                                "type": "array",
                                "description": "Ordered steps to prepare the recipe.",
                                "items": {
                                    "type": "string",
                                    "description": "Description of a preparation step.",
                                },
                            },
                        },
                        "required": ["title", "ingredients", "steps"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["cocktails", "sideDishes"],
            "additionalProperties": False,
        },
    },
}


def get_recipes(client: OpenAI, beverage: BeveragePublic) -> tuple[str, ChatCompletionMessage]:
    tags = [tag.name for tag in beverage.tags]
    beverage_description = (
        f"It's name is {beverage.title}, described as {beverage.description}, "
        f"it belongs to the category {beverage.category.name} and has the "
        f"following properties: {', '.join(tags)}."
    )
    user_message = (
        f"I want to know what to do with this beverage. {beverage_description} "
        f"Can you help me with a cocktail recipe? Also, please provide some dishes to pair with it."
    )
    system_role = (
        "You are a bartender and a chef. You can provide cocktail and meal recipes. "
        "You can only provide at most 2 recipes for each."
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": user_message},
        ],
        response_format=GET_RECIPES_JSON_SCHEMA,
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return beverage_description, response.choices[0].message
