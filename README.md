
<p align="center">
    <img src="./assets/logo.png" alt="WESE Logo" width="150">
    <br>
    <strong style="font-size: 36px;">WESE</strong>
</p>

# Introduction

WESE (Well-founded Explanations for Stable Extensions in Abstract Argumentation Framework) is a tool designed to explain stable extensions using provenance tracking and visualization techniques. It helps users understand how stable extensions are derived based on the following logical rule under stable semantics:

$$
\text{Defeated}(x) \leftarrow \text{Attacks}(y, x), \neg \text{Defeated}(y).
$$

# Usage 

## Website
You can directly visit the following website to use the tool
https://wese-app.onrender.com

## Locally development
Install the necessary package
```bash
pip install -r requirements.txt
python app.py
```
before deployment, you need to test by running
```bash
gunicorn app:server
```

# License
The software is available under the MIT license.


# Acknowledgment
WESE is built upon [PyArg](https://github.com/DaphneOdekerken/PyArg)

# Contact
For any queries, please open an issue on GitHub or contact [Yilin Xia](https://yilinxia.com/)