//Tela de Login

const inputs = document.querySelectorAll(".input-field");
const toggle_btn = document.querySelectorAll(".toggle");
const main = document.querySelector("main");
const bullets = document.querySelectorAll(".bullets span");
const images = document.querySelectorAll(".image");

inputs.forEach((inp) => {
  inp.addEventListener("focus", () => {
    inp.classList.add("active");
  });
  inp.addEventListener("blur", () => {
    if (inp.value != "") return;
    inp.classList.remove("active");
  });
});

toggle_btn.forEach((btn) => {
  btn.addEventListener("click", () => {
    main.classList.toggle("sign-up-mode");
  });
});

function moveSlider() {
  let index = this.dataset.value;

  let currentImage = document.querySelector(`.img-${index}`);
  images.forEach((img) => img.classList.remove("show"));
  currentImage.classList.add("show");

  const textSlider = document.querySelector(".text-group");
  textSlider.style.transform = `translateY(${-(index - 1) * 2.2}rem)`;

  bullets.forEach((bull) => bull.classList.remove("active"));
  this.classList.add("active");
}

bullets.forEach((bullet) => {
  bullet.addEventListener("click", moveSlider);
});

document.addEventListener('DOMContentLoaded', function () {
    if (!localStorage.getItem('termosAceitos')) {
        document.getElementById('termoResponsabilidade').style.display = 'block';
    }


    document.getElementById('aceitarTermos').addEventListener('click', function () {
        localStorage.setItem('termosAceitos', 'true');
        document.getElementById('termoResponsabilidade').style.display = 'none';
    });
});

function atualizarPrecos() {
  fetch('/atualizar_precos')
  .then(response => response.json())
  .then(data => {

      for (const [sigla, info] of Object.entries(data)) {
          document.querySelector(`#preco-${sigla}`).textContent = `$${info.preco.toFixed(2)}`;
          document.querySelector(`#volume-${sigla}`).textContent = `$${info.volume.toLocaleString()}`;
          const percentual = document.querySelector(`#percentual-${sigla}`);
          percentual.textContent = `${info.percentual_variacao.toFixed(2)}%`;
          percentual.className = info.percentual_variacao > 0 ? 'verde' : 'vermelho';
      }
  })
  .catch(error => console.error('Erro ao atualizar os preços:', error));
}

setInterval(atualizarPrecos, 10000);

document.addEventListener('DOMContentLoaded', atualizarPrecos);



document.addEventListener('DOMContentLoaded', function () {
  let paginaAtual = 1;
  const feedbacksPorPagina = 6;

  carregarFeedbacks();

  document.getElementById('enviar-feedback').addEventListener('click', function () {
      const nome = document.getElementById('nome').value;
      const mensagem = document.getElementById('mensagem').value;

      if (nome && mensagem) {
          const feedback = { nome, mensagem };
          salvarFeedback(feedback);
          atualizarFeedbacks();

          document.getElementById('nome').value = '';
          document.getElementById('mensagem').value = '';
      } else {
          alert('Por favor, preencha todos os campos!');
      }
  });

  function salvarFeedback(feedback) {
      let feedbacks = localStorage.getItem('feedbacks');
      feedbacks = feedbacks ? JSON.parse(feedbacks) : [];
      feedbacks.push(feedback);
      localStorage.setItem('feedbacks', JSON.stringify(feedbacks));
  }

  function carregarFeedbacks() {
      atualizarFeedbacks();
  }

  function atualizarFeedbacks() {
      let feedbacks = localStorage.getItem('feedbacks');
      feedbacks = feedbacks ? JSON.parse(feedbacks) : [];
      const totalPaginas = Math.ceil(feedbacks.length / feedbacksPorPagina);
      mostrarFeedbacks(feedbacks, paginaAtual);
      criarBotoesPaginacao(totalPaginas);
  }

  function mostrarFeedbacks(feedbacks, pagina) {
      const listaFeedbacks = document.getElementById('lista-feedbacks');
      listaFeedbacks.innerHTML = '';

      const inicio = (pagina - 1) * feedbacksPorPagina;
      const fim = inicio + feedbacksPorPagina;
      const feedbacksPagina = feedbacks.slice(inicio, fim);

      feedbacksPagina.forEach(feedback => {
          const divFeedback = document.createElement('div');
          divFeedback.className = 'feedback';
          divFeedback.innerHTML = `<p>“${feedback.mensagem}” - ${feedback.nome}</p>`;
          listaFeedbacks.appendChild(divFeedback);
      });
  }

  function criarBotoesPaginacao(totalPaginas) {
      const paginacaoContainer = document.getElementById('paginacao');
      paginacaoContainer.innerHTML = '';

      for (let i = 1; i <= totalPaginas; i++) {
          const paginaNumero = document.createElement('span');
          paginaNumero.innerText = i;
          paginaNumero.addEventListener('click', function () {
              paginaAtual = i;
              atualizarFeedbacks();
          });

          if (i === paginaAtual) {
              paginaNumero.classList.add('ativo');
          }

          paginacaoContainer.appendChild(paginaNumero);
      }
  }
});


document.addEventListener("DOMContentLoaded", function () {
  const feedbackBom = document.querySelector(".feedback-bom");
  const feedbackRuim = document.querySelector(".feedback-ruim");
  const feedbackUsuarioDiv = document.querySelector(".feedback-usuario");

  feedbackBom.addEventListener("click", function () {
      mostrarMensagem("Obrigado pelo seu feedback positivo sobre " + '{{ cripto }}' + "!");
  });

  feedbackRuim.addEventListener("click", function () {
      mostrarMensagem("Obrigado pelo seu feedback negativo sobre " + '{{ cripto }}' + ".");
  });

  function mostrarMensagem(mensagem) {
      const mensagemDiv = document.createElement("p");
      mensagemDiv.textContent = mensagem;
      mensagemDiv.style.fontWeight = "bold";
      mensagemDiv.style.color = "#28a745"; // Verde para feedback positivo
      feedbackUsuarioDiv.appendChild(mensagemDiv);

      // Remover mensagem após 3 segundos
      setTimeout(() => {
          feedbackUsuarioDiv.removeChild(mensagemDiv);
      }, 3000);
  }
});


function iniciarPrevisao() {
    const periodoHistorico = document.getElementById('periodo-historico').value;
    const intervaloDados = document.getElementById('intervalo-dados').value;
    const periodoPrevisao = document.getElementById('periodo-previsao').value;

    fetch(`/previsao/{{ cripto }}?periodo=${periodoHistorico}&intervalo=${intervaloDados}&dias=${periodoPrevisao}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            cripto: '{{ cripto }}',
            periodo_historico: periodoHistorico,
            intervalo_dados: intervaloDados,
            periodo_previsao: periodoPrevisao
        })
    })
    .then(response => response.json())
    .then(data => {
        // Aqui você pode processar e exibir os dados retornados da previsão
        document.getElementById('resultado-previsao').innerHTML = data.resultado; // Ajuste conforme necessário
    })
    .catch(error => console.error('Erro ao iniciar a previsão:', error));
}

let contagemBom = 0; // Contagem de votos bons
let contagemRuim = 0; // Contagem de votos ruins

function darFeedback(tipo) {
    if (tipo === 'bom') {
        contagemBom++;
        const largura = (contagemBom / (contagemBom + contagemRuim)) * 100;
        document.getElementById('barra-bom').style.width = largura + '%';
    } else {
        contagemRuim++;
        const largura = (contagemRuim / (contagemBom + contagemRuim)) * 100;
        document.getElementById('barra-ruim').style.width = largura + '%';
    }
    
    // Atualizar contagem
    document.getElementById('contagem-bom').innerText = `${contagemBom} votos Bom`;
    document.getElementById('contagem-ruim').innerText = `${contagemRuim} votos Ruim`;
}


    