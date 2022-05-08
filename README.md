#### Semogong_plot

세상의 모든 공부, 대쉬보드 페이지 제작을 위한 파이썬 Matplotlib 코드

분석화면 : http://semogong.site/data

#### 구성

- Python
- MySQL
- S3
- Docker
- Kubernetes cronjobs


#### k8s Cronjob
Cron job을 이용해서 일정시간마다, 차트가 갱신되게 변경

Cron : '0 * * * *'

(변경 전) 한국시간 기준 새벽 4시에 실행되기를 원하며, UTC와 9시간 차이기에, 4 - 9 = -19 로 변경
(변경 후) 1시간마다 업데이트 하도록 설정 
