---
trigger: model_decision
description: Quando for criar ou alterar testes unitários com pytest/Python
globs:
---

# Diretrizes gerais para testes unitários

- Ao nomear funções de teste, se o módulo já possuir outros testes, siga o padrão de nomenclatura dos testes já existentes. Caso não exista nenhum teste, utilize o padrão snake_case para o nome dos testes, iniciando com o prefixo `test_`.
- Ao criar classes de teste, o nome da classe de teste deve **SEMPRE** seguir o padrão de usar o nome da classe sob teste, mais o prefixo "Test". Por exemplo: { classe: "Foo", classeDeTeste: "TestFoo" }
- Não escreva comentários nos testes.
- Separe os blocos Arrange, Act e Assert (quando houver) por uma linha em branco.
- Não utilize métodos ou classes deprecated de libs como pytest, unittest.mock nos testes.
- Restringir o uso de mock utilizando apenas métodos da biblioteca unittest.mock nas classes de teste.
- Ao criar testes nunca modifique o código de produção para fazer esses testes passarem.
- Testes devem validar comportamento observável das classes sob teste (efeitos colaterais, mudanças de estado, retorno, delegação), e não afirmar ausência de lógica.
- Os testes devem testar os comportamentos observáveis da classe através da API pública dessa classe, evitando aumentar a visibilidade de métodos privados (com prefixo `_`) só para testá-los.
