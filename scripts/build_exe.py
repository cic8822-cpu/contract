import PyInstaller.__main__
import os
import sys

def build_exe():
    # 현재 파일 위치 기준 루트의 main.py 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_script = os.path.join(base_dir, 'main.py')
    
    # PyInstaller 옵션 설정
    # --onefile: 단일 실행 파일
    # --noconsole: 실행 시 콘솔 창 숨김
    # --clean: 빌드 전 캐시 삭제
    # --name: 생성될 파일 이름
    
    PyInstaller.__main__.run([
        main_script,
        '--onefile',
        '--noconsole',
        '--clean',
        '--name=신규채용_계약서_자동화_v1.0',
        '--distpath=' + os.path.join(base_dir, 'dist'),
        '--workpath=' + os.path.join(base_dir, 'build'),
        '--specpath=' + base_dir,
    ])

if __name__ == "__main__":
    build_exe()
