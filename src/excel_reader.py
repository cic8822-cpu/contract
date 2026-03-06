import pandas as pd
import os

def read_hiring_data(file_path):
    """
    채용자 명단 엑셀 파일을 읽어 데이터를 반환합니다.
    헤더: 순, 직종, 수험번호, 이름, 생일, 전화, 임용일, 주소
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    
    # 엑셀 파일 로드
    df = pd.read_excel(file_path)
    
    # 컬럼명 정리 (공백 제거 등)
    df.columns = [col.strip() for col in df.columns]
    
    # 데이터를 딕셔너리 리스트로 변환
    data_list = df.to_dict(orient='records')
    
    return data_list

if __name__ == "__main__":
    # 테스트 코드
    try:
        sample_path = "신규채용자 서류접수_26.3.9..xlsx"
        if os.path.exists(sample_path):
            data = read_hiring_data(sample_path)
            print(f"총 {len(data)}명의 데이터를 읽어왔습니다.")
            print(f"첫 번째 데이터: {data[0]}")
    except Exception as e:
        print(f"에러 발생: {e}")
