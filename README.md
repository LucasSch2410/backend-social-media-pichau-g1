<h1 align="center">Backend Social Media Pichau</h1>

<br />

<h2 align="center" id="env">Instalando pacotes:</h2>

```bash
pip install -r requirements.txt
```

<br />

<h2 align="center">Criando variáveis de ambiente:</h2>

<p>Crie um arquivo .env na raiz do projeto e atribua as variáveis indicadas no arquivo config.py</p>


<h3>Criação do Refresh Token:</h3>

<a href="https://www.dropboxforum.com/t5/Dropbox-API-Support-Feedback/Get-refresh-token-from-access-token/td-p/596739
" target="_blank">Criação do Refresh Token pelo Dropbox Forum</a>


<br />

<h2 align="center">Inicializando o servidor:</h2>

<h3>Uvicorn</h3>

```bash
uvicorn app.main:app --reload
```

<br />

<h2 align="center" id="doc">Documentação da API</h2>

<p>Depois de ter iniciado o servidor, acesse a documentação da API para mais informações.</p>

<a href="http://localhost:8000/docs" target="_blank">Documentação 1</a>
<br/>
<a href="http://localhost:8000/redoc" target="_blank">Documentação 2</a>
<br/>


<h2 align="center" id="doc">Documentação das principais dependências</h2>

<a href="https://dropbox-sdk-python.readthedocs.io/en/latest/" target="_blank">Dropbox SDK</a>
<br/>
<a href="https://devdocs.io/fastapi/" target="_blank">FastAPI</a>
<br/>
<a href="https://developers.google.com/docs/api/quickstart/python?hl=pt-br">Google Cloud</a>