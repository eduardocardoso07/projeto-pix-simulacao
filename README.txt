PIX Lab — demonstração antifraude com geolocalização OPT-IN

IMPORTANTE
- O comprovante é deliberadamente identificado como SIMULAÇÃO e não imita de forma indistinguível um banco real.
- A localização só é obtida depois que o usuário clica no botão e aceita a permissão do navegador.
- Depois da autorização, a coordenada é enviada para POST /location no servidor do laboratório.
- O servidor grava apenas a coordenada, precisão e timestamps em locations.jsonl.
- Use somente em dispositivos/pessoas que tenham consentido com o teste.

COMO RODAR
1. Instale Python 3.11+.
2. No diretório do projeto:
   python -m venv .venv
   .venv\Scripts\activate       (Windows)
   pip install -r requirements.txt
   python app.py
3. Abra http://127.0.0.1:8000

PARA TESTAR PELO CELULAR / OUTRO DISPOSITIVO
Geolocation exige contexto seguro (HTTPS), com exceção de localhost.
Para um teste remoto, publique o projeto em um servidor HTTPS sob seu controle
(por exemplo, uma hospedagem que forneça TLS). Não use um link público para
coletar localização de pessoas que não tenham consentido.

COMO VER AS COORDENADAS
Após um teste, cada linha de locations.jsonl contém latitude e longitude.
Para transformar em um ponto no mapa, copie as coordenadas para um mapa de sua
escolha. Evite registrar IP, user-agent ou outros identificadores se eles não
forem necessários para o estudo.

PARA UM LABORATÓRIO DE SEGURANÇA
Uma boa prática é mostrar ao participante, depois do teste, exatamente:
- qual permissão foi solicitada;
- que a coordenada foi enviada;
- qual dado foi recebido;
- por quanto tempo ele ficará armazenado.
