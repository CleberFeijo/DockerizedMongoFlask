# 1988 Brazilian constituition article extractor

## This application has the purpose of locating, extracting and storing the brazilian constitution laws articles from a PDF.

## System developed in Python, using Flask as it's web framework, MongoDB as it's database and Docker for the services disponibilization.

To use the application you need to:

Install docker with:

    https://docs.docker.com/engine/install/ubuntu/

After that, you need to clone the repository:

    git clone git@gitlab.com:cleberfeijo/DockerizedMongoFlask.git

To start the application, open your terminal in the directory where you cloned the files and use:

    docker-compose up -d
(-d so everything runs on the background)

After installed, you may just put the code on the app directory in the file 'app.py'. Then to access the API use:

    http://localhost:80

To access the articles extraction API use:

    http://localhost:80/extrair
(It may take a while to all the articles to get extracted and stored, you'll be warned when it ends!)

To access the articles database checking API use:

    http://localhost:80/artigos

To stop the application use:

    docker-compose down

