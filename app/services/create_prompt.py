def create_system_prompt(
        prompt_template_path: str,
        markdown_template_path: str,
        css_template_path: str,
) -> str:
    """
    Create a prompt for the summarization model.

    Args:
        prompt_template_path (str): Path to the prompt template file.
        markdown_template_path (str): Path to the markdown template file.
        css_template_path (str): Path to the CSS template file.

    Returns:
        str: The generated prompt.
    """
    # Read prompt template
    with open(prompt_template_path, 'r') as file:
        prompt_template = file.read()

    # Read markdown template
    with open(markdown_template_path, 'r') as file:
        markdown_template = file.read()

    # Read CSS template
    with open(css_template_path, 'r') as file:
        css_template = file.read()

    # Replace placeholders in prompt template
    prompt = prompt_template.replace('{{MARKDOWN_TEMPLATE}}', markdown_template)
    prompt = prompt.replace('{{CSS_TEMPLATE}}', css_template)

    return prompt
