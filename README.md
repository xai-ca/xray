<div align="center">
    <img src="./assets/logo.png" alt="WESE Logo" width="150">
    <h1 align="center">WESE</h1>
    <h3> Well-founded Explanations for Stable Extensions in Abstract Argumentation Framework </h3>
</div>

[![deploy](https://github.com/idaks/wese-app/actions/workflows/deploy.yml/badge.svg)](https://github.com/idaks/wese-app/actions/workflows/deploy.yml)


![alt text](./assets/demo.png)

# Overview

WESE (Well-founded Explanations for Stable Extensions in Abstract Argumentation Framework) is a tool designed to explain stable extensions using provenance tracking and visualization techniques. It helps users understand how stable extensions are derived based on the following logical rule under stable semantics:

$$
\text{Defeated}(x) \leftarrow \text{Attacks}(y, x), \neg \text{Defeated}(y).
$$

# Usage 

## Website
You can access the tool by visiting the following website (https://wese.onrender.com) directly. Please note that it may take some time to load, as the service automatically shuts down after long periods of inactivity.


## Locally Development
> [!TIP]
> It is recommended to use a Conda environment.

Install the necessary package

```bash
git clone https://github.com/idaks/wese-app
conda create -n wese-app python=3.10
conda activate wese-app
conda install anaconda::graphviz
cd wese-app
pip install -r requirements.txt
python app.py
```
<!-- before deployment, you can test by running
```bash
gunicorn app:server
``` -->

## Docker Manually Deployment
Rebuild the Docker Image
```bash
docker buildx build --platform linux/amd64 -t seanyl/wese:app .
```

Push the image to docker hub
```
docker push seanyl/wese:app
```

# License
The software is available under the MIT license.


# Acknowledgment
WESE is built upon [PyArg](https://github.com/DaphneOdekerken/PyArg)

# Contact
For any queries, please open an issue on GitHub or contact [Yilin Xia](https://yilinxia.com/)