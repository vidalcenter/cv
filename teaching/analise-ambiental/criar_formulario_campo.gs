/**
 * Script para criar o "Formulário para Trabalho de Campo" no Google Drive.
 *
 * COMO USAR:
 * 1. Acesse https://script.google.com (logado como ldvsantos@uefs.br)
 * 2. Clique em "New project"
 * 3. Apague o código padrão e cole ESTE arquivo inteiro
 * 4. Clique em "Run" (▶) e aceite as permissões
 * 5. O formulário será criado no seu Drive e a URL aparecerá no log (View → Logs)
 *
 * O script:
 *   - Cria o formulário com todas as seções e campos obrigatórios
 *   - Coleta automaticamente o e-mail do respondente
 *   - Mostra as URLs de edição e de resposta ao final
 */

function createFormularioTrabalhoDeCampo() {
  var form = FormApp.create('Formulário para Trabalho de Campo');

  // ========== DESCRIÇÃO INICIAL ==========
  form.setDescription(
    'INFORMAÇÕES BÁSICAS PARA REALIZAÇÃO DE TRABALHO DE CAMPO. ' +
    'O ESTUDANTE DEVERÁ PREENCHER O FORMULÁRIO COM TODAS AS INFORMAÇÕES.\n\n' +
    'A FALTA DE INFORMAÇÕES BÁSICAS IMPLICARÁ NA IMPOSSIBILIDADE DE ' +
    'CADASTRAMENTO DO ESTUDANTE NO TRABALHO DE CAMPO.'
  );

  // Coleta automática do e-mail institucional
  form.setCollectEmail(true);

  // ========== SEÇÃO 1: IDADE ==========
  form.addSectionHeaderItem()
    .setTitle('Necessidade de Autorização para viagem de menor desacompanhado')
    .setHelpText(
      'Estudantes menores de idade deverão procurar o(a) professor(a) ' +
      'responsável para assinatura da Autorização para viagem de menor desacompanhado'
    );

  var idadeItem = form.addMultipleChoiceItem();
  idadeItem.setTitle('IDADE')
    .setRequired(true)
    .setChoices([
      idadeItem.createChoice('+18'),
      idadeItem.createChoice('Menor de 18 anos')
    ]);

  // ========== SEÇÃO 2: DADOS PARA ANEXO IV ==========
  form.addSectionHeaderItem()
    .setTitle('DADOS PARA ANEXO IV - Formulário de solicitação de atividade de campo')
    .setHelpText('Preenchimento de Nome completo, matrícula e RG.');

  form.addTextItem()
    .setTitle('NOME COMPLETO')
    .setRequired(true);

  form.addTextItem()
    .setTitle('MATRÍCULA')
    .setRequired(true);

  form.addTextItem()
    .setTitle('NÚMERO RG OU CPF OU PASSAPORTE')
    .setRequired(true);

  form.addTextItem()
    .setTitle('ORGÃO EMISSOR DO DOCUMENTO')
    .setRequired(true);

  // ========== SEÇÃO 3: INFORMAÇÕES GERAIS E DE SAÚDE ==========
  form.addSectionHeaderItem()
    .setTitle('Informações gerais e de saúde do(a) participante');

  form.addTextItem()
    .setTitle('NOME COMPLETO SEM ABREVIAÇÃO')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Número de Matrícula')
    .setRequired(true);

  var sanguineoItem = form.addMultipleChoiceItem();
  sanguineoItem.setTitle('TIPO SANGUÍNEO')
    .setRequired(true)
    .setChoices([
      sanguineoItem.createChoice('A+'),
      sanguineoItem.createChoice('A-'),
      sanguineoItem.createChoice('B+'),
      sanguineoItem.createChoice('B-'),
      sanguineoItem.createChoice('AB+'),
      sanguineoItem.createChoice('AB-'),
      sanguineoItem.createChoice('O+'),
      sanguineoItem.createChoice('O-'),
      sanguineoItem.createChoice('Não sei')
    ]);

  form.addTextItem()
    .setTitle('Alergias a Medicamentos (caso sim, especificar)')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Outras alergias (caso sim, especificar)')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Doenças crônicas (caso sim, especificar)')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Uso de Medicação Controlada (caso sim, especificar)')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Plano de Saúde')
    .setRequired(true);

  form.addDateItem()
    .setTitle('Data de Nascimento')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Endereço Residencial')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Telefone')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Religião')
    .setRequired(true);

  form.addTextItem()
    .setTitle('CONTATO DE EMERGÊNCIA - NOME DA PESSOA')
    .setRequired(true);

  form.addTextItem()
    .setTitle('CONTATO DE EMERGÊNCIA - TELEFONE DA PESSOA')
    .setRequired(true);

  form.addTextItem()
    .setTitle('CONTATO DE EMERGÊNCIA - GRAU DE PARENTESCO DA PESSOA')
    .setRequired(true);

  // ========== RESULTADO ==========
  Logger.log('✅ Formulário criado com sucesso!');
  Logger.log('📝 URL de edição: ' + form.getEditUrl());
  Logger.log('📋 URL para respondentes: ' + form.getPublishedUrl());
  Logger.log('');
  Logger.log('Copie a URL de respondentes acima e compartilhe com os alunos.');
}
