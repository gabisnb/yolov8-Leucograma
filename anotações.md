# Experimento 1:
Feito sem balancear o dataset, com conjunto de treino e de teste

- Treino: SlashP, MaluP, 523P, 519P, UrasP, MagreloP, NathyP, NathyG, NinaG, PretinhaG, TobyG, NegaoG, SlashG, CarameloG, GaiaG
- Teste: 517P, LobinhoG, JujubaG, CristalG
- Validação: 459P, DuqueP

## Dataset
Número total de imagens: 1992

### Contagem de indivíduos por classe:
- neutrofilo: 2014
- linfocito: 925
- monocito: 269
- bastonete: 301
- metamielocito: 33
- eosinofilo: 533
- metarrubricito: 15

Resultados: runs/detect/sem balanceamento/

# Experimento 2:
Feito balanceando o dataset, com o mesmo conjunto de treino e de teste.
Leve melhora na precisão do monócito e do bastonete.

## Balanceamento
Número total de imagens: 937

### Contagem de indivíduos por classe:
- neutrofilo: 947
- linfocito: 503
- monocito: 251
- bastonete: 271
- metamielocito: 32
- eosinofilo: 260
- metarrubricito: 12

Resultados: runs/detect/com balanceamento/900 neutrofilos

# Experimento 3:
Feito balanceando o dataset, consertou problemas que havia em algumas imagens e anotações, trocou Duque para treino e Cristal foi para validação.
Treinamento parece ter convergido em 90 épocas e dado overfitting na classe eosinófilo

- Treino: SlashP, MaluP, 523P, 519P, UrasP, MagreloP, NathyP, NathyG, NinaG, PretinhaG, TobyG, NegaoG, SlashG, CarameloG, GaiaG, DuqueP
- Teste: 517P, LobinhoG, JujubaG
- Validação: 459P, CristalG

## Balanceamento
Número total de imagens: 778

### Contagem de indivíduos por classe:
- neutrofilo: 618
- linfocito: 373
- monocito: 231
- bastonete: 245
- metamielocito: 33
- eosinofilo: 259
- metarrubricito: 15

Resultados: runs/detect/com balanceamento/600 neutrofilos
