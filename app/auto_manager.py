import subprocess
import time
import sys

def run_cycle():
    cycle_count = 1
    
    while True:
        print(f"\n⚡ CICLO #{cycle_count}: MODO OPERACIÓN (TRADING)")
        print("Bot iniciado. Operando por 12 horas (Maratón)...")
        
        # 1. Iniciar Bot
        # Usamos Popen para no bloquear
        # Added -u for unbuffered output to see logs in real-time
        bot_process = subprocess.Popen([sys.executable, "-u", "-m", "app.bot"])
        
        try:
            # WATCHDOG LOOP
            # En lugar de dormir 4 horas seguidas, dormimos en bloques de 10s
            # y verificamos si el bot sigue vivo.
            OPERATING_TIME = 43200 # 12 Horas 
            elapsed = 0
            
            while elapsed < OPERATING_TIME:
                if bot_process.poll() is not None:
                    print("⚠️ ALERTA: El Bot se murió inesperadamente. Reviviéndolo... 🚑")
                    bot_process = subprocess.Popen([sys.executable, "-u", "-m", "app.bot"])
                
                time.sleep(10)
                elapsed += 10
            
        except KeyboardInterrupt:
            print("Manager detenido. Matando bot...")
            if bot_process.poll() is None:
                bot_process.terminate()
            break
            
        # 2. Hora de Dormir (Power Nap)
        print("\n💤 HORA DE DORMIR: Deteniendo Bot para Power Nap...")
        bot_process.terminate()
        bot_process.wait()
        
        print(f"🔄 INICIANDO APRENDIZAJE (Ciclo #{cycle_count})")
        
        # A. Refrescar Datos
        print("1. Descargando memoria reciente...")
        subprocess.run([sys.executable, "-m", "app.refresh_data"])
        
        # B. Re-Entrenar
        print("2. Re-calibrando Red Neuronal Transformer...")
        subprocess.run([sys.executable, "-m", "app.train_transformer"])
        
        # C. Safety Check (Nuevo)
        # Verificar si estamos perdiendo demasiado
        # Necesitamos leer balance.
        # Por simplicidad, si el usuario nos avisa de perdidas, mejor poner un hard-stop manual.
        # Pero podemos agregar un "Panic Button" si el archivo 'STOP' existe.
        if os.path.exists("STOP_BOT"):
            print("🛑 SEÑAL DE PARADA DETECTADA. Terminando ciclo.")
            break
            
        print("✅ ENTRENAMIENTO COMPLETADO. El Bot es más inteligente ahora.")
        print("Reiniciando operaciones en 5 segundos...")
        time.sleep(5)
        
        cycle_count += 1

if __name__ == "__main__":
    run_cycle()
