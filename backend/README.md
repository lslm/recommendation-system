## Subindo a API com Docker

### Crie a imagem
```shell
    docker build -t news_recommendation .
```

### Inicie o Container, e acesse http://localhost:8000/docs

```shell
    docker run -d -p 8000:8000 --name recommendation_container news_recommendation
```