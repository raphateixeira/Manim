import subprocess
import shutil
import os
import time
from pathlib import Path
import platform

# ===== CONFIGURAR AQUI =====
SCRIPT_NAME = "VetoresNoR2.py"
CLASS_NAME = "VectoresNoR2"
QUALITY = 'h'  # 'l'=480p15 | 'm'=720p30 | 'h'=1080p60
# ==========================

def render_manim_scene(script_name, class_name, quality):
    """Renderiza cena Manim e limpa arquivos temporários."""
    
    current_dir = Path.cwd()
    media_dir = current_dir / "media"
    videos_dir = media_dir / "videos"
    
    print(f"🎬 Renderizando {class_name}...")
    subprocess.run([
        "manim",
        f"-q{quality}",
        "--media_dir", str(media_dir),
        "--disable_caching",
        script_name,
        class_name
    ], check=True)
    
    time.sleep(1)
    
    # Procurar MP4 recursivamente
    mp4_file = None
    if videos_dir.exists():
        mp4_files = list(videos_dir.rglob("*.mp4"))
        if mp4_files:
            mp4_file = mp4_files[0]
    
    if mp4_file:
        output_path = current_dir / f"{class_name}.mp4"
        shutil.copy2(str(mp4_file), str(output_path))
        print(f"✅ Vídeo: {output_path.name}")
        
        time.sleep(0.5)
        if platform.system() == "Darwin":
            os.system(f"open '{output_path}'")
        elif platform.system() == "Windows":
            os.startfile(output_path)
        else:
            os.system(f"xdg-open '{output_path}'")
    else:
        print("⚠️  MP4 não encontrado")
    
    # Limpar
    time.sleep(0.5)
    if media_dir.exists():
        shutil.rmtree(media_dir)
    pycache = current_dir / "__pycache__"
    if pycache.exists():
        shutil.rmtree(pycache, ignore_errors=True)
    
    print("✨ Pronto!")

if __name__ == "__main__":
    render_manim_scene(SCRIPT_NAME, CLASS_NAME, QUALITY)