import requests

def buscar_endereco_cep(cep):

    cep = cep.replace("-", "")
    url = f"https://viacep.com.br/ws/{cep}/json/"
    consulta = requests.get(url)
    if consulta.status_code != 200:
        return None
    data = consulta.json()
    if data.get("erro"):
        return None

    return {
        "cep": data.get("cep"),
        "estado": data.get("uf"),
        "cidade": data.get("localidade"),
        "bairro": data.get("bairro"),
        "logradouro": data.get("logradouro"),
    }