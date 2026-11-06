##---------------------------------------------------------------------------
# [필요한 함수 호출]
from pathlib import Path
import csv
import json
import torch
from torch import nn
# nn: 신경망의 계층, 활성화 함수, 손실 함수 등을 사용하기 위해 호출
from torch.utils.data import TensorDataset, DataLoader
##---------------------------------------------------------------------------



##---------------------------------------------------------------------------
# [파일 경로 읽기]
base = Path(__file__).resolve().parent  # 현재 폴더의 절대경로
out = base / "outputs"                  # 결과물을 저장할 경로
out.mkdir(exist_ok=True)                # 폴더가 없으면 생성할 것
##---------------------------------------------------------------------------



##---------------------------------------------------------------------------
# [데이터 읽기]
with (base / "data" / "points.csv").open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
# CSV의 각 행에 대해서 열 이름을 키로 갖는 딕셔너리로 읽기
# rows = ... : 모든 행을 리스트에 저장하기

train_rows = [r for r in rows if r["split"] == "train"] # train행 추출
valid_rows = [r for r in rows if r["split"] == "valid"] # valid행 추출

X_train = torch.tensor([[float(r["x1"]), float(r["x2"])] for r in train_rows])
# for r in train_rows: 각 행을 하나씩 가져온 후
# [float(r["x1"]), float(r["x2"])] "x1", "x2"에 해당하는 값을 묶어서 리스트로 만들기
# torch.tensor(): Pytorch tensor로 변환하기(2차원의 행렬이 된다.)

y_train = torch.tensor([int(r["label"]) for r in train_rows], dtype=torch.long)
# dtype=torch.long: 데이터자료형을 64비트 정수로 저장한다. (큰 정수를 다루기 위함이다.)
# 하지만 현재 코드에서는 정답이 0과 1이라서 큰 수를 다루기 위함은 아니고, CE가 정답 클래스를 int64형태로 요구하기 때문이다.
# 즉, dtype=torch.long는 CE를 쓰기 때문에 붙이는 것

X_valid = torch.tensor([[float(r["x1"]), float(r["x2"])] for r in valid_rows])
y_valid = torch.tensor([int(r["label"]) for r in valid_rows], dtype=torch.long)
##---------------------------------------------------------------------------


##---------------------------------------------------------------------------
# [환경 설정]
torch.manual_seed(42)
# 난수 설정
# 난수를 연구자들이 동일하게 42로 설정하면 난수의 생성순서와 값이 동일하게 나타난다.
# 이를 통해 모델 학습 결과를 비교하기 쉽게 만든다.

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# cuda를 사용할 수 있으면 "cuda:0"을, 사용하지 못하면 cpu를 device에 할당함
# 실제로 이 단계에서 GPU 및 CPU에 모델이 이동되는 것은 아니고, 이동은 다음 코드에서

loader = DataLoader(TensorDataset(X_train, y_train), batch_size=32, shuffle=True,
                    generator=torch.Generator().manual_seed(43), num_workers=0)
# TensorDataset(X_train, y_train): 입력값과 정답지를 하나로 묶는 과정
# batch_size=32: 한 번에 가져오는 데이터의 개수를 최대 32개로 설정
#                '최대'라고 한 이유는 데이터가 100개인 경우 32, 32, 32, 4개가 되기 때문
# shuffle=True: epoch마다 학습 데이터의 순서를 무작위로 섞음
#               특정 순서의 영향을 받는 것을 배제하기 위함
# generator=torch.Generator().manual_seed(43): 난수 생성기. torch.manual_seed(42)와 동일한 역할
# num_workers=0: 별도 프로세스 없이 현재 프로세스에서 처리한다는 뜻
#                CPU, GPU 할당을 의미하는 것이아니라, 보조 프로세스를 쓰는지 여부일 뿐이다.
# 해당 코드는 결국, 학습에 필요한 데이터 셋을 준비 및 설정을 하는 것

model = nn.Sequential(nn.Linear(2, 8), nn.ReLU(), nn.Linear(8, 2)).to(device)
# 신경망 설정(오늘 학습 중 중요사항!)
# nn.Linear(2, 8): 입력 특성 2개 받아 은닉층의 활성화 함수에 들어갈 값 8개 계산
# nn.ReLU: 은닉층의 활성화 함수로 ReLU 적용하기
# nn.Linear(8, 2): 은닉층의 출력 8개 받아 최종 클래스 점수 2개 계산
# 그 결과 실습의 문제인 0과 1이 출력되는 것이 아니라 logits이 출력됨 예)logits = [1.2, 3.5]

loss_fn = nn.CrossEntropyLoss()
# Loss 계산을 위해 CE를 사용함
# 이진 분류 문제는 BCE를 사용해도 되지만, 현재 신경망 설정의 마지막 출력층이 nn.Linear(8, 2)로 하여서 출력 2개를 내보내는 CE를 사용하는 것이 나아보인다.
# 만약 BCE를 선택한다면 출력이 클래스 1에 대한 확률만 출력되기 때문에 신경망 및 차원 일치 문제가 생긴다.

optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
# 확률적 경사하강법 사용(batch size가 설정되어 있으므로 정확히는 mini-batch SGD 방식이다.)
# model.parameter(): 업데이트할 모델의 가중치(weight) 및 편향(bias) 전달
# 학습률은 0.1로 설정

Xv, yv = X_valid.to(device), y_valid.to(device)
# 검증 데이터를 할당된 device(CPU 혹은 GPU로 이동)
Xt, yt = X_train.to(device), y_train.to(device)
##---------------------------------------------------------------------------



##---------------------------------------------------------------------------
# [실제 학습]
history = []
for epoch in range(81):
# 총 시행 횟수(epoch): 80회
# 81인 이유는 0번째는 모델의 초기 성능 측정하는 것이라 실제 학습이 아니기 때문.
    if epoch > 0:
        model.train()
        # 위에서 만들었던 신경망 설정을 학습모드로 전환
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            #####################################
            # [오늘 학습에서 제일 중요한 단계]
            optimizer.zero_grad()
            # 그래디언트값 초기화      
            loss = loss_fn(model(xb), yb)
            # CE loss 함수 계산(순전파)
            loss.backward()
            # 역전파 계산
            optimizer.step()
            # 모델의 파라미터(weight, bias) 업데이트
            #####################################
##---------------------------------------------------------------------------



##---------------------------------------------------------------------------
# [기록 및 출력]
    if epoch % 10 == 0:
        # 10번째마다 모델로 계산한 손실과 정확도를 기록
        model.eval()
        # 이번에는 모델을 평가모드로 전환(학습한 가중치 유지된 채로)
        with torch.no_grad():
            train_loss = loss_fn(model(Xt), yt).item()
            # 학습 데이터 손실 계산
            logits = model(Xv)
            # 검증 데이터에 대한 로짓 계산
            valid_loss = loss_fn(logits, yv).item()
            # 검증 데이터 손실 계산
            accuracy = (logits.argmax(dim=1) == yv).float().mean().item()
            # 검증 데이터 정확도 계산(새로운 데이터에 대한 정확도가 의미있으므로 검증 데이터에 대해서만)
        history.append([epoch, train_loss, valid_loss, accuracy])
        # 각 결과를 history 리스트에 저장하기
        print(epoch, round(train_loss, 6), round(valid_loss, 6), round(accuracy, 4))
        # 출력
##---------------------------------------------------------------------------



##---------------------------------------------------------------------------
# [csv 파일로 저장]
with (out / "training_history.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["epoch", "train_loss_eval", "valid_loss", "valid_accuracy"])
    writer.writerows(history)
##---------------------------------------------------------------------------



##---------------------------------------------------------------------------
# [최종 결과 검증 및 파일 저장]
model.eval()
with torch.no_grad():
    logits = model(Xv)
    predictions = logits.argmax(dim=1).cpu()
metrics = {"device": str(device), "torch": str(torch.__version__), "epochs": 80,
           "train_rows": len(train_rows), "valid_rows": len(valid_rows), "test_used": False,
           "initial_train_loss": history[0][1], "final_train_loss": history[-1][1],
           "valid_loss": history[-1][2], "valid_accuracy": history[-1][3]}
(out / "final_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
with (out / "validation_predictions.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f); writer.writerow(["id", "actual", "predicted"])
    writer.writerows((r["id"], int(y), int(p)) for r, y, p in zip(valid_rows, y_valid, predictions))
(out / "gpu_check.txt").write_text(
    f"torch={torch.__version__}\ncuda_build={torch.version.cuda}\n"
    f"cuda_available={torch.cuda.is_available()}\nselected_device={device}\n", encoding="utf-8")
print("생성: outputs의 환경·학습·검증 결과")

errors = []
for r, actual, predicted in zip(valid_rows, y_valid, predictions):
    if int(actual) != int(predicted):
        errors.append((r["id"], int(actual), int(predicted)))
with (out / "validation_errors.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "actual", "predicted"])
    writer.writerows(errors)
print("valid 오답 수:", len(errors))
##---------------------------------------------------------------------------
# [결과 출력]
# 0 0.565832 0.510637 0.7
# 10 0.331469 0.281476 0.975
# 20 0.228078 0.182579 0.975
# 30 0.176405 0.134341 1.0
# 40 0.145632 0.105641 1.0
# 50 0.12504 0.086818 1.0
# 60 0.110228 0.074174 1.0
# 70 0.098804 0.064484 1.0
# 80 0.089844 0.057217 1.0
# 생성: outputs의 환경·학습·검증 결과
# valid 오답 수: 0
##---------------------------------------------------------------------------
# [결과 해석]
# 검증 데이터가 40개로 적고, 최종 테스트는 아직 하지 않은 상황이라 단정하기 어렵지만,
# 검증 정확도가 100%에 도달한 30번째가 유의미한 것으로 보인다. 이후 에포크는 학습 개선효과 없음
# 하지만 검증 손실은 80까지도 줄었으므로 과적합 징후는 보이지 않았다.
##---------------------------------------------------------------------------