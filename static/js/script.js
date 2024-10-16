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
    // Verifica se o usuário já aceitou os termos
    if (!localStorage.getItem('termosAceitos')) {
        // Exibe o modal de responsabilidade
        document.getElementById('termoResponsabilidade').style.display = 'block';
    }

    // Ação quando o usuário clica em "Aceitar e Continuar"
    document.getElementById('aceitarTermos').addEventListener('click', function () {
        // Salva a aceitação no localStorage
        localStorage.setItem('termosAceitos', 'true');
        // Oculta o modal
        document.getElementById('termoResponsabilidade').style.display = 'none';
    });
});

document.addEventListener('DOMContentLoaded', function () {
    // Carrega feedbacks salvos
    carregarFeedbacks();

    // Adiciona evento de envio de feedback
    document.getElementById('enviar-feedback').addEventListener('click', function () {
        const nome = document.getElementById('nome').value;
        const mensagem = document.getElementById('mensagem').value;

        if (nome && mensagem) {
            const feedback = {
                nome: nome,
                mensagem: mensagem,
            };
            
            salvarFeedback(feedback);
            adicionarFeedbackNaTela(feedback);

            // Limpa o formulário
            document.getElementById('nome').value = '';
            document.getElementById('mensagem').value = '';
        } else {
            alert('Por favor, preencha todos os campos!');
        }
    });
});

function salvarFeedback(feedback) {
    let feedbacks = localStorage.getItem('feedbacks');
    feedbacks = feedbacks ? JSON.parse(feedbacks) : [];
    feedbacks.push(feedback);
    localStorage.setItem('feedbacks', JSON.stringify(feedbacks));
}

function carregarFeedbacks() {
    let feedbacks = localStorage.getItem('feedbacks');
    feedbacks = feedbacks ? JSON.parse(feedbacks) : [];
    feedbacks.forEach(feedback => {
        adicionarFeedbackNaTela(feedback);
    });
}

function adicionarFeedbackNaTela(feedback) {
    const listaFeedbacks = document.getElementById('lista-feedbacks');
    const divFeedback = document.createElement('div');
    divFeedback.className = 'Feedback';
    divFeedback.innerHTML = `<p>“${feedback.mensagem}” - ${feedback.nome}</p>`;
    listaFeedbacks.appendChild(divFeedback);
}
