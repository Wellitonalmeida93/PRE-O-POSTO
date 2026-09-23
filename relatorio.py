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

# ATENÇÃO: Coloque aqui o link da primeira aba (Visão Geral/Gráficos)
URL_POWER_BI_1 = "https://app.powerbi.com/view?r=eyJrIjoiNWU1OTNjYzctODQ4OS00MWU1LTgwNzUtNjExODhiZDU5MjU3IiwidCI6ImY0Y2Q4NWNjLWQ1YTAtNGVmZC04NzkzLThhNzg5NDE5MGNmYSJ9&pageName=11dd9b00ac155a080748"

# ATENÇÃO: Coloque aqui o link da segunda aba (Acordos/Tabela)
URL_POWER_BI_2 = "https://app.powerbi.com/view?r=eyJrIjoiNWU1OTNjYzctODQ4OS00MWU1LTgwNzUtNjExODhiZDU5MjU3IiwidCI6ImY0Y2Q4NWNjLWQ1YTAtNGVmZC04NzkzLThhNzg5NDE5MGNmYSJ9&pageName=b9c5c1c000a792559110" 

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

def enviar_email(caminho_img1, caminho_img2):
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

        # HTML do E-mail (Formatado como um relatório profissional)
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
                        <a href="{URL_POWER_BI_1}" style="display: inline-block; background-color: #0056b3; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 13px;">
                            Acessar Dashboard Online
                        </a>
                    </p>

                    <!-- IMAGEM 1: VISÃO GERAL -->
                    <div style="margin-top: 40px;">
                        <h3 style="background-color: #f4f6f9; padding: 10px 15px; border-left: 4px solid #1a365d; color: #333; margin-bottom: 15px; font-size: 16px;">
                            📈 1. Comparativo de Mercado e Curva de Preços
                        </h3>
                        <div style="text-align: center;">
                            <img src="cid:img_visao_geral" style="width: 100%; max-width: 850px; border: 1px solid #ddd; border-radius: 6px;">
                        </div>
                    </div>

                    <!-- IMAGEM 2: ACORDOS -->
                    <div style="margin-top: 40px;">
                        <h3 style="background-color: #fdf5f5; padding: 10px 15px; border-left: 4px solid #d9534f; color: #333; margin-bottom: 15px; font-size: 16px;">
                            ⚠️ 2. Análise de Acordos e Divergências
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

        # Anexando as duas imagens chamando a função auxiliar que criamos
        anexar_imagem(msg, caminho_img1, "img_visao_geral", "visao_geral.png")
        anexar_imagem(msg, caminho_img2, "img_acordos", "analise_acordos.png")

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
    
    # Define o caminho onde as duas imagens serão salvas
    img_pagina_1 = os.path.join(pasta_script, "print_visao_geral.png")
    img_pagina_2 = os.path.join(pasta_script, "print_acordos.png")

    # 1. Captura a primeira tela
    sucesso_1 = capturar_print_powerbi(URL_POWER_BI_1, img_pagina_1, "VISÃO GERAL")
    if not sucesso_1:
        print("🛑 Falha ao capturar página 1 do dashboard.")
        sys.exit(1)

    # 2. Captura a segunda tela
    sucesso_2 = capturar_print_powerbi(URL_POWER_BI_2, img_pagina_2, "ANÁLISE DE ACORDOS")
    if not sucesso_2:
        print("🛑 Falha ao capturar página 2 do dashboard.")
        sys.exit(1)

    # 3. Envia o e-mail com as duas imagens
    sucesso_email = enviar_email(img_pagina_1, img_pagina_2)
    if not sucesso_email:
        print("🛑 Falha ao enviar e-mail.")
        sys.exit(1)

    print("🎉 PROCESSO CONCLUÍDO COM SUCESSO")
