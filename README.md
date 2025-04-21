# Octa Music

Projeto Flask para buscar artistas no Spotify.

## Instalação

1. Clone o repositório.
2. Crie um ambiente virtual:
   ```
   python -m venv venv
   ```
3. Ative o ambiente virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
5. Copie o arquivo `.env.example` para `.env` e preencha com suas credenciais do Spotify.

## Execução

```
python src/main.py
```

Acesse [http://localhost:5000](http://localhost:5000) no navegador.

## Configuração

As credenciais do Spotify devem estar no arquivo `.env`:

```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```
