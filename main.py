"""Mini NPU Simulator의 콘솔 실행 진입점을 제공한다."""

from mini_npu.modes import run_mode1


def main() -> None:
    """메뉴를 출력하고 사용자가 선택한 실행 모드로 연결한다."""
    print("=== Mini NPU Simulator ===")
    print("\n[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    print("3. 패턴 생성기 / 최적화 비교 (보너스)")

    choice = input("선택: ").strip()
    if choice == "1":
        run_mode1()
    elif choice in ("2", "3"):
        print("선택한 모드는 다음 구현 단계에서 제공됩니다.")
    else:
        print("잘못된 선택입니다. 1, 2, 3 중 하나를 입력하세요.")


if __name__ == "__main__":
    main()
