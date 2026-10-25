# EEA 人間承認・署名の境界 R001

- 公開日：2026-10-25 JST
- 区分：公開施工要領・設計原則の説明（実署名の完了証明ではない）
- 関連：[EEA 2026年10月見直し](EEA_OCTOBER_2026_PUBLIC_REVIEW.md)
- 状態：設計説明を公開。専用操作盤、鍵登録、実署名・実配備の検収は別工程

## 1. まず人間が何をすればよいか

人間の行為を、最低でも次の3つに分ける。

| 行為 | 人間が行うこと | 成立する状態 |
|---|---|---|
| 通常の可逆施工の直接発注 | 対象と施工範囲を明示して指示する | 当該範囲の施工依頼。暗号署名・受入ではない |
| 検収・受入 | 図番、固定版、試験結果、残HOLDを確認し、受入範囲を明示する | 別のHuman受入証票。必要な本人認証を伴うが、暗号署名とは限らない |
| 例外・高影響操作の承認 | 操作盤に表示された作用・対象・上限・期限を確認し、本人専用の鍵を解除して「この内容を1回だけ承認」を実行する | 検証可能な署名付き**別Artifact**。本人署名が実行され、検証を通過した場合に限る |

人間の指示や認証済みコメントは**本人の意思表示の証拠になり得る**が、暗号署名を生成した事実そのものではない。AIが作成した文書、PR、氏名入力、メールアドレス入力、会話上の「承認」、テスト鍵、署名形式のJSONを実署名と呼ばない。

## 2. 署名用操作盤に必要な最小表示

```text
図番・発注番号
操作（具体的な作用と副作用）
対象（固定したArtifact/版/hash、台帳・作業目的）
最大費用（通貨を含む）／実費上限 0
有効期限
適用範囲と残るHOLD/UNKNOWN
[差戻し]  [この内容を1回だけ承認]
```

操作盤は、Hostが実際の台帳・固定版・証憑から作成した対象を表示する。Workerが書いた説明文だけから対象を決めない。画面は当該Workerから改変できない信頼境界に置く。

本人は表示内容を確認し、**自分の鍵を自分で解除**して署名する。利用者へhash、署名文字列、JSON、鍵素材を手入力させない。画面の確認だけ、または「承認」ボタンを押しただけで署名が生成されなかった場合は `NOT_SIGNED` とする。

## 3. 検証器側で確認する事項

既設のローカル実装候補はEd25519署名の照合を採用している。ただし、特定の実装が実運用に適合したと本書は認定しない。最低限、以下を独立に確認する。

1. Human本人に対応する登録公開鍵で、署名対象の**正確なバイト列**を検証する。本人秘密鍵はWorkerに渡さない。
2. 操作・対象版・作業目的・証憑チェックポイント・範囲・期限・費用上限が、Hostが要求した対象と一致する。
3. 承認が有効期間内で、鍵・承認IDが失効しておらず、失効状態自体も確認済みである。
4. 承認IDは一回限り。再使用、すり替え、別環境での使い回しを拒否する。
5. 署名済みArtifact、検証結果、本人受入、元のAI Draftを別記録として保全する。

```text
AI_DRAFT != HUMAN_ACCEPTANCE
AUTHENTICATED_COMMENT != CRYPTOGRAPHIC_SIGNATURE
SIGNATURE_VERIFIED != FACT_VERIFIED
AUTHORITY_GRANTED != HOLD_CLEARED
PUBLICATION != CANONICAL_ADOPTION
```

本人鍵の初回登録は人間管理下で行い、信頼済み操作環境で本人を確認する。AIが人間の秘密鍵を生成・保持・解除・代理署名してはならない。秘密鍵をGitHub、ログ、プロンプト、配布ZIPへ保存しない。

## 4. 権限の段階とSTOP

- 可逆・低影響な所有者管理下の限定施工は、明示された直接発注の範囲で継続できる。毎回の暗号署名を通常作業の前提としない。
- 本番公開、有料API呼出し、不可逆・高影響な作用、権限例外、署名済み例外照合は、それぞれの対象・作用を明示し、必要な別Human Gateを通す。ある工区の承認を別工区へ継承しない。
- 人間のSTOPは署名成立を待たず実行できる。停止解除、再開、例外復旧は別条件で確認する。
- 本人が署名しても、原資料の真正性・試験の未施工・未確認をPASSに変えない。

## 5. 証票の状態

```text
DRAFTED
  -> PRESENTED_TO_HUMAN
  -> HUMAN_ACTED
  -> CRYPTOGRAPHIC_SIGNATURE_CREATED
  -> INDEPENDENTLY_VERIFIED
  -> AUTHORITY_BOUND_TO_EXACT_SCOPE
  -> EXECUTED_OR_HOLD
```

途中で止まった場合は、最後に確認された状態と未実施工程を記録する。「鍵登録の予定」「承認依頼を表示」「署名書式を作成」は `SIGNATURE_CREATED` ではない。

この署名方式の暗号学的成立は、特定法域の法的電子署名要件・契約上の効力を自動的に保証しない。法的効力が必要な工区は、該当制度の適用要件を別途検証する。

## 6. 今回の公開と未実施事項

本書は2026-10-25の所有者の明示的な資料公開指示に基づき公開する。これは**説明文書を公開するための直接指示**であり、本人のEd25519署名が完了したとの記録ではない。

実Human鍵登録・署名操作・独立した検証試験は、別工区で完了証票が提出されるまで `NOT_EXECUTED / HOLD` とする。公開文章によってAIが自ら承認権限を獲得することはない。

## English summary

A direct human instruction, human acceptance, and a cryptographically signed exception are distinct acts. A valid signature requires a human-controlled key, an exact fixed scope, a visible deliberate action, and independent signature verification. Chat text, draft documents, or synthetic signatures are not real human signatures.
