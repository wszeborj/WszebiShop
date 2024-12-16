* [General info])(#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [More detailed information about modules](#more-detailed-information-about-modules)
* [Application view](#application-view)


## General info
<details>
<summary>Click here to see general information about <b>Project</b>!</summary>
<b>WszebiShop</b>. is an e-commerce platform designed to simplify the buying and selling of products.
The application allow users profile management, product management including searching and filtering products,
payment process integrated with Stripe, and order management.
The project is built using modern tools and frameworks like Django, Django Framework, Plotly Dash
ensuring scalability and high performance.
</details>

## Tools & Technologies
<ul>
<li>Python</li>
<li>Django</li>
<li>Bootstrap4</li>
<li>PostgreSQL</li>
<li>Plotly</li>
<li>Stripe</li>
<li>Requests</li>
<li>Sentry</li>
<li>unittest</li>
<li>Pre-commit</li>
<li>Docker-Compose & Docker</li>
<li>Poetry</li>
</ul>

## Setup
Clone the repo
```bash
git clone https://github.com/wszeborj/WszebiShop
```
Go to project folder
```bash
cd wszebishop
```
Install poetry
```bash
pip install poetry
```
Install all modules
```bash
poetry install
```
Migrate
```bash
poetry run python manage.py migrate
```
Run application
```bash
poetry run python manage.py runserver
```
Run tests
```bash
poetry run python manage.py test
```

## Application features
<ul>
<li>create, update user</li>
<li>create, update, remove products</li>
<li>create, update orders</li>
<li>filter products by categories</li>
<li>filter orders by status</li>
<li>searching for products</li>
<li>Stripe payment integration</li>
<li>Product image management</li>
<li>Interactive data visualizations (e.g., sales analysis)</li>

</ul>

## Application View
<ul>
<li>main</li>
<img src="https://github.com/user-attachments/assets/37ae69d1-c892-46bd-bc97-a3e28b477721" width="50%" height="50%"></img>
<li>product view</li>
<img src="https://github.com/user-attachments/assets/9c9030cb-d28a-4345-a49a-dafe768af6fe" width="50%" height="50%"></img>
<li>cart view</li>
<img src="https://github.com/user-attachments/assets/f07ef83d-3609-487a-97f4-1526427fdc46" width="50%" height="50%"></img>
<li>order confirmation view</li>
<img src="https://github.com/user-attachments/assets/02bf3fa5-cf5a-4d1a-8517-8ee5ee403eb1" width="50%" height="50%"></img>
