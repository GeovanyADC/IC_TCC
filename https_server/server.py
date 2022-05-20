"""
    COMANDOS PARA ACESSAR A API LOCALMENTE
    - fazer o encaminhamento de porta desta porta para a porta que seu aplicativo está escutando no WSL
    - netsh interface portproxy add v4tov4 listenport=8432 listenaddress=0.0.0.0 connectport=8432 connectaddress=192.168.84.128
    - connectaddress=(172.30.65.138) IP do WSL
    - Adicionar uma regra de entrada no firewall do windows
    - Manualmente ou com o código:
    - netsh advfirewall firewall add rule name="Allowing LAN connections" dir=in action=allow protocol=TCP localport=8432
    - Acessar a página como ipv4 do pc -> 192.168...

    SENHA DO PGADMIN - 5492200
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "industrial_production.main:app",
        host="0.0.0.0",
        port=8432,
        # port=8000,
        reload=True,
        ssl_keyfile="./key.pem",
        ssl_certfile="./cert.pem",
    )
