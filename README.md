# Extrator de Artigos da constituição brasileira de 1988
## Aplicação com o propósito de localizar, extrair e armazenar os artigos de leis da constituição brasileira de 1988 a partir de um PDF.

## Sistema desenvolvido em Python, utilizando Flask como framework web, MongoDB como banco de dados e o Docker para a disponibilização dos serviços.

Para utilização da aplicação é necessário:

instalar o docker seguindo:

    https://docs.docker.com/engine/install/ubuntu/

Depois, clonar o repositório:

    git clone git@gitlab.com:cleberfeijo/DockerizedMongoFlask.git

Para iniciar a aplicação, abra o terminal no diretorio onde clonou os arquivos e use:

    docker-compose up -d
(-d para tudo ser feito em segundo plano)

Depois de instalado basta colocar o código no diretorio app no arquivo app.py e para acessar a api:

    http://localhost:80

Para acessar a api de extração de artigos:

    http://localhost:80/extrair

Para acessar a api para checar os artigos no banco de dados:

    http://localhost:80/artigos

Para destruir/parar a aplicação:

    docker-compose down

