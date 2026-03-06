from pyhwpx import Hwp
import os

class HwpContractWriter:
    def __init__(self, visible=False):
        self.hwp = Hwp(visible=visible)

    def fill_contract(self, template_path, data, output_path):
        """
        한글 양식 파일에 데이터를 채우고 개별 저장합니다.
        data: {'이름': '...', '생일': '...', ...} 형태의 딕셔너리
        """
        try:
            # 양식 파일 열기
            self.hwp.open(template_path)
            
            # 1. 누름틀(Field) 방식 데이터 입력
            fields = self.hwp.get_field_list().split('\x02')
            
            # 2. 데이터 매핑 및 입력
            for key, value in data.items():
                str_value = str(value) if value is not None and str(value) != 'nan' else ""
                
                # 누름틀이 있는 경우 우선 입력
                if key in fields:
                    self.hwp.put_field_text(key, str_value)
                
                # {{변수}} 형태의 텍스트 치환 (누름틀이 없는 경우 대비)
                placeholder = f"{{{{{key}}}}}"  # {{변수}} 형태
                self.hwp.find_replace_all(placeholder, str_value)
            
            # 개별 파일로 저장
            self.hwp.save_as(output_path)
            self.hwp.FileClose()
            return True
        except Exception as e:
            print(f"파일 생성 중 에러 발생 ({output_path}): {e}")
            return False

    def quit(self):
        self.hwp.quit()

if __name__ == "__main__":
    # 테스트 코드 (실제 실행 시 한글 프로그램이 설치되어 있어야 함)
    # writer = HwpContractWriter(visible=True)
    # writer.fill_contract("양식.hwp", {"이름": "테스트"}, "결과.hwp")
    # writer.quit()
    pass
