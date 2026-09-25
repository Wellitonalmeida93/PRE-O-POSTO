import os
import sys
import time
import traceback
import smtplib
from datetime import datetime, timedelta

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from playwright.sync_api import sync_playwright

# ==================================================
# CONFIGURAÇÕES
# ==================================================

# Link do Power BI - Segunda Aba (Acordos/Tabela)
URL_POWER_BI = "https://app.powerbi.com/view?r=eyJrIjoiNWU1OTNjYzctODQ4OS00MWU1LTgwNzUtNjExODhiZDU5MjU3IiwidCI6ImY0Y2Q4NWNjLWQ1YTAtNGVmZC04NzkzLThhNzg5NDE5MGNmYSJ9&pageName=11dd9b00ac155a080748" 

REMETENTE_EMAIL = "welliton.almeida@pizzattolog.com.br"
REMETENTE_SENHA = os.environ.get("SENHA_EMAIL")

DESTINATARIOS = [
    "welliton.almeida@pizzattolog.com.br"
]

SMTP_SERVIDOR = "smtp.gmail.com"
SMTP_PORTA = 587

# ==================================================
# CAPTURA DO POWER BI
# ==================================================

def capturar_print_powerbi(url, caminho_saida, nome_etapa):
    print("=" * 60)
    print(f"📸 INICIANDO CAPTURA: {nome_etapa}")
    print("=" * 60)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()
            page.set_default_timeout(120000)

            print(f"🌐 Abrindo dashboard ({nome_etapa})...")
            page.goto(url, wait_until="domcontentloaded", timeout=120000)

            print("⏳ Aguardando renderização dos gráficos...")
            time.sleep(60)

            print("📷 Capturando screenshot...")
            page.screenshot(path=caminho_saida, full_page=True)

            browser.close()

            if not os.path.exists(caminho_saida):
                print(f"❌ Screenshot {nome_etapa} não foi criada.")
                return False

            tamanho = os.path.getsize(caminho_saida)
            print(f"✅ Screenshot {nome_etapa} criada. (Tamanho: {tamanho:,} bytes)")

            if tamanho < 10000:
                print("⚠️ Screenshot muito pequena.")
                return False

            return True

    except Exception:
        print(f"\n❌ ERRO AO CAPTURAR O POWER BI ({nome_etapa})")
        traceback.print_exc(file=sys.stdout)
        return False

# ==================================================
# ENVIO DE E-MAIL
# ==================================================

def anexar_imagem(msg, caminho_arquivo, cid_nome, nome_arquivo):
    """Função auxiliar para anexar imagens ao corpo do email"""
    with open(caminho_arquivo, "rb") as arquivo:
        imagem = MIMEImage(arquivo.read())
        imagem.add_header("Content-ID", f"<{cid_nome}>")
        imagem.add_header("Content-Disposition", "inline", filename=nome_arquivo)
        msg.attach(imagem)

def enviar_email(caminho_img):
    print("=" * 60)
    print("📧 PREPARANDO E ENVIANDO E-MAIL")
    print("=" * 60)

    try:
        if not REMETENTE_SENHA:
            print("❌ SENHA_EMAIL não encontrada.")
            return False

        msg = MIMEMultipart("related")
        msg["From"] = REMETENTE_EMAIL
        msg["To"] = ", ".join(DESTINATARIOS)
        
        data_ontem = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
        msg["Subject"] = f"📊 Relatório Diário de Valores Negociados - POSTOS - {data_ontem}"

        # HTML do E-mail
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px 0;">
                
                <div style="max-width: 900px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                    
                    <!-- CABEÇALHO -->
                    <h2 style="color: #1a365d; text-align: center; border-bottom: 2px solid #1a365d; padding-bottom: 15px; margin-top: 0;">
                        Relatório Diário de Valores Negociados
                    </h2>
                    
                    <p style="text-align: center; color: #555; font-size: 14px;">
                        Resumo atualizado referente ao dia <strong>{data_ontem}</strong>.<br>
                        <br>
                        <a href="{URL_POWER_BI}" style="display: inline-block; background-color: #0056b3; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 13px;">
                            Acessar Dashboard Online
                        </a>
                    </p>

                    <!-- IMAGEM: ACORDOS -->
                    <div style="margin-top: 40px;">
                        <h3 style="background-color: #fdf5f5; padding: 10px 15px; border-left: 4px solid #d9534f; color: #333; margin-bottom: 15px; font-size: 16px;">
                            ⚠️ Análise de Acordos e Divergências
                        </h3>
                        <p style="color: #666; font-size: 13px; margin-bottom: 15px;">
                            Atenção aos postos com status <strong>"Acima do Acordo"</strong> ou <strong>"Sem Acordo"</strong>.
                        </p>
                        <div style="text-align: center;">
                            <img src="cid:img_acordos" style="width: 100%; max-width: 850px; border: 1px solid #ddd; border-radius: 6px;">
                        </div>
                    </div>

                    <!-- RODAPÉ -->
                    <div style="margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #999; font-size: 12px;">
                        <p>
                            Este é um relatório automático gerado pelo sistema.<br>
                            Em caso de dúvidas, consulte o painel completo no Power BI.
                        </p>
                    </div>

                </div>

            </body>
        </html>
        """

        msg.attach(MIMEText(html, "html", "utf-8"))

        # Anexando apenas a imagem de Acordos
        anexar_imagem(msg, caminho_img, "img_acordos", "analise_acordos.png")

        print("📡 Conectando Gmail SMTP...")
        with smtplib.SMTP(SMTP_SERVIDOR, SMTP_PORTA, timeout=60) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()

            print("🔑 Realizando login...")
            server.login(REMETENTE_EMAIL, REMETENTE_SENHA)

            print("📤 Enviando e-mail...")
            server.sendmail(REMETENTE_EMAIL, DESTINATARIOS, msg.as_string())

        print("✅ E-mail enviado com sucesso.")
        return True

    except Exception:
        print("\n❌ ERRO AO ENVIAR E-MAIL")
        traceback.print_exc(file=sys.stdout)
        return False

# ==================================================
# EXECUÇÃO
# ==================================================

if __name__ == "__main__":
    print("🚀 INICIANDO PROCESSO")

    pasta_script = os.path.dirname(os.path.abspath(__file__))
    
    # Caminho do print
    img_acordos = os.path.join(pasta_script, "print_acordos.png")

    # 1. Captura apenas a tela de Acordos
    sucesso = capturar_print_powerbi(URL_POWER_BI, img_acordos, "ANÁLISE DE ACORDOS")
    if not sucesso:
        print("🛑 Falha ao capturar página do dashboard.")
        sys.exit(1)

    # 2. Envia o e-mail
    sucesso_email = enviar_email(img_acordos)
    if not sucesso_email:
        print("🛑 Falha ao enviar e-mail.")
        sys.exit(1)

    print("🎉 PROCESSO CONCLUÍDO COM SUCESSO")
