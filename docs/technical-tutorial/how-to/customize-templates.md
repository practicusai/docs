---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Practicus AI Code Generation Templates

Practicus AI workers use **Jinja2 templates** in ~/practicus/templates folder to streamline and automate code generation for key components such as Python libraries, Airflow DAGs and Jupyter notebooks. This approach ensures consistency, scalability, and customization across your projects. Below is an overview of how these templates work and how you can use them effectively.

---

## 1. **Overview of Jinja2 Templates**
Jinja2 is a powerful templating engine for Python, enabling dynamic creation of files by inserting variables and logic into predefined structures. In our platform, templates are configured to:
- Standardize code structure and style.
- Dynamically generate project-specific code.
- Simplify the onboarding process for new workflows.
- To learn more please visit:
    - https://jinja.palletsprojects.com/en/stable/intro/

---

## 2. **How to Customize Templates**
- Start a worker and view templates in ~/practicus/templates folder
- Customize templates by editing the Jinja2 syntax with your specific project details.
- Templates can be rendered to test programmatically, see below a sample.
- Once your testing is completed, you can create a new Practicus AI worker container image and override existing template files.
---

## 3. **Best Practices**
- **Test Before Use:** Validate generated code in a test environment.
- **Document Changes:** If you modify templates, document the changes for future reference.
- **Leverage Variables and Logic:** Use Jinja2's advanced features like loops and conditionals for maximum flexibility.

```python
# Jinja templates in action..

from jinja2 import Template

template_content = """
def {{ function_name }}(x):
    return x ** 2
"""

template = Template(template_content)
rendered_code = template.render(function_name="square")
print(rendered_code)

# prints
# def square(x):
#    return x ** 2
```


---

**Previous**: [Work With Data Catalog](work-with-data-catalog.md) | **Next**: [Configure Advanced Gpu](configure-advanced-gpu.md)
