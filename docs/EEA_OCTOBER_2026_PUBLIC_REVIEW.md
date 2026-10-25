# EEA 2026年10月見直し — 公開別紙 R001

- 公開日：2026-10-25 JST
- 区分：PUBLIC REVIEW MATERIAL / NOT NORMATIVE ADOPTION
- 対象：EEA v1.0 Draft の運用評価・測定方法の見直し
- 既存本文：`EEA_v1.0_Draft.md` は不変更
- 安全憲法：Version 0.2 Draft は不変更
- 公開根拠：2026-10-25の所有者による明示的な公開指示（暗号署名の完了を意味しない）
- 制約：観測候補の採用・HOLD解除・実配備検収を、本書公開から推定しない

## 1. 今回公開する内容

EEAの設計順序は引き続き次のとおりである。

```text
責任
  ↓
介入点
  ↓
境界・権限・証跡
  ↓
受入検査
```

2026年9月19〜20日の複数AI Workerを用いた施工・統合・独立照査の観測を、10月の見直し材料として整理した。今回の公開は**観測方法と検査候補の開示**であり、12候補をEEAの新原則に採用したという意味ではない。2026年10月19日を予定日とした憲法層の独立した最終受入検査が完了した証明も含まない。

## 2. 測点を潰さない見直し

```text
RAW OBSERVATION PRESERVED
  → PROVISIONAL CLUSTERING
  → CONSTRAINT-SURFACE HYPOTHESIS
  → REVIEW
  → ADOPT / HOLD / REJECT
```

- **観測事実と原因推定を分離**する。中断は疲労の証明ではない。認証失敗・利用枠不足・工具不良をモデル能力不足へ一括計上しない。
- 生の測点、発生時刻、対象版、依存、反証、UNKNOWN、過去の失敗を保存する。仮クラスタから元の測点に戻れるようにする。
- 類似する事象を同一原因と断定しない。仮クラスタは分析補助であり、証拠でも権限でもない。
- 複数の独立測点が同じ境界を拘束する場合に限り、制約面を仮説として構成する。同一試験器・同一実装に由来する相関を独立証憑として数えない。
- 反例・時間差・補修前後の対象版を照合する。後の成功で過去の失敗を消さない。

最小測点項目：`id / observed_fact / observed_at / source_artifact / source_commit / workface / actor_or_worker / triggering_conditions / dependencies / observed_effect / reproducibility / counterevidence / unknowns / current_state`。

```text
OBSERVATION != CAUSE
PROVISIONAL_CLUSTER != SAME_CAUSE
PROVISIONAL_CLUSTER != EEA_PRINCIPLE
TEST_PASS != SYSTEM_CLOSURE
```

## 3. 10月の12見直し候補

以下は**検査・測定・付録への分類候補**であり、新しい義務・規格・合格判定ではない。

| ID | 見直し候補 | 検査上の論点 |
|---|---|---|
| C-01 | 単体評価と施工系評価 | 個別Workerだけでなく、統合・引継ぎ・独立検査を含めた評価単位 |
| C-02 | Humanの管理と詳細介入 | 目的・権限・STOP条件の指定と、個々の作業指図量を別軸にする |
| C-03 | 統合照査 | 局所PASSと工区全体の閉包を混同しない |
| C-04 | 連続施工と中断 | 中断・再開・工区分割を測り、原因を擬人化して確定しない |
| C-05 | 環境要因 | 認証・利用枠・工具・モデルの不適合を区別する |
| C-06 | 既設状態の読戻し | 新しい作業区画で正本・発注・差分から施工状態を再構成する |
| C-07 | 独立竣工照査 | 自己試験のPASSで独立検査を代替しない |
| C-08 | 意味結合 | 否定・疑問・欠落・不確実性と対象の結合を測る |
| C-09 | 表示境界 | 内部情報の非露出と、利用者に必要な意味の保持を両立する |
| C-10 | 下位作業編成と権限 | 工区編成の委任を公開・正本発行権限の拡大と扱わない |
| C-11 | 小補修と第三者検査 | 統合担当者による小補修を独立竣工検査の代わりにしない |
| C-12 | 局所HOLD | 支障のある工区を止め、独立した工区は証拠に基づき継続する |

特に次を保持する。

```text
SELF_TEST_PASS != INDEPENDENT_INSPECTION_PASS
LOCAL_WORKER_PASS != SYSTEM_CLOSURE
SUBORDINATE_STRUCTURE_DISCRETION != AUTHORITY_EXPANSION
BOUNDARY_SANITIZATION != SEMANTIC_ERASURE
LOCAL_HOLD != GLOBAL_STOP
```

## 4. 受入・権限境界の追補

一般の可逆な作業に毎回の人間署名を要求すると、Human Gateが施工停止の原因になる。一方、公開・課金・不可逆操作・権限例外では、対象を固定し、独立した人間の判断を確認する必要がある。

- 直接発注、受入検査、暗号署名を同一の状態としない。
- **能力・信用・ログイン・過去の承認から新しい権限を自動発生させない**。
- 署名は、承認対象と作用を人間が確認して実際に署名したときだけ成立する。AIが署名用JSONを作ったことは署名ではない。
- 署名があっても、未測定項目のPASSやUNKNOWN/HOLDの自動解除にはならない。
- 人間の停止要求には、事前の技術的証明や署名を要求しない。

具体的な人間操作、認証済み受入と暗号署名の区別、署名対象、失効・再利用防止は[人間承認・署名の境界 R001](HUMAN_APPROVAL_AND_SIGNATURE_20261025.md)を参照する。

## 5. 判定範囲と未閉包

本別紙の公開によって、次の事項は成立しない。

- 10月候補のEEA本文への採用、憲法改正、規格制定
- 各候補の全件測定完了、独立照査のPASS、全域の安全性保証
- 現地環境における署名器の完成・本人鍵の登録・本人署名
- 別工区のHOLD/UNKNOWNの解除
- 公開・課金・外部作用の自動権限付与

今後の正式採用では、各候補を`OBSERVATION_ONLY / OPERATIONAL_TEST_CANDIDATE / MEASUREMENT_SCHEMA_CANDIDATE / APPENDIX_CANDIDATE / PRINCIPLE_REVISION_CANDIDATE / HOLD / REJECTED`へ分類し、必要な独立照査と人間の別承認を経て本文を改訂する。

**本別紙の公開状態は `PUBLIC`、EEA原則への採用状態は `NOT_ADOPTED` である。**

## English summary

This October 2026 public review note preserves raw observations, distinguishes provisional clusters from causal claims, and lists twelve evaluation candidates for multi-worker engineering workflows. It does not revise EEA v1.0 Draft or the Safety Constitution. Human work instructions, acceptance, and cryptographically signed authority are separate acts; no real signature or deployment acceptance is claimed by this publication.
