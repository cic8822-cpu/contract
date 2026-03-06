from src.excel_reader import read_hiring_data
from src.hwpx_writer import HwpContractWriter
import os

def run_contract_automation(excel_path, template_path, output_dir, progress_callback=None):
    """
    전체 계약서 생성 프로세스를 실행합니다.
    """
    # 1. 출력 디렉토리 확인 및 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 2. 엑셀 데이터 로드
    data_list = read_hiring_data(excel_path)
    total = len(data_list)
    
    # 3. 한글 제어 인스턴스 생성
    writer = HwpContractWriter(visible=False)
    
    success_count = 0
    try:
        for i, data in enumerate(data_list):
            # 파일명 생성 규칙: [임용일] 직종-이름-계약서.hwp
            # 엑셀 컬럼명에 따라 수정 필요 (임용일, 직종, 이름)
            name = data.get('이름', '무명')
            job = data.get('직종', '직종미정')
            hire_date = str(data.get('임용일', '날짜미상')).split(' ')[0] # 날짜만 추출
            
            # 특수문자 제거 (파일명용)
            safe_name = "".join([c for c in name if c.isalnum() or c in (' ', '-', '_')])
            
            filename = f"[{hire_date}] {job}-{safe_name}-계약서.hwp"
            output_path = os.path.join(output_dir, filename)
            
            # 계약서 작성
            if writer.fill_contract(template_path, data, output_path):
                success_count += 1
            
            # 진행 상황 업데이트 (GUI 연동용)
            if progress_callback:
                progress_callback(i + 1, total, f"작성 중: {filename}")
        
        return True, f"총 {total}명 중 {success_count}명의 계약서를 생성했습니다."
    
    except Exception as e:
        return False, f"작업 중 에러 발생: {e}"
    
    finally:
        writer.quit()

if __name__ == "__main__":
    # 테스트 실행
    pass
