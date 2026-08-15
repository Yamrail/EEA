# YamRail 証憑束＋正本管理 施工例（Private Staging）

> **日本語正文 / Japanese text is authoritative.**  
> 本READMEは日本語を正文とし、後半の英語は参考訳です。

このディレクトリは、公開前の人間検収を目的として作成した**架空の土木施工例**です。実案件のデータは使用していません。

## 目的

本施工例では、次の事項を分離して管理する形を示します。

- 施工票
- 原証憑
- 出来形照査
- HOLD（未確認・保留）
- 現行正本
- 正本候補
- 変更履歴
- Human Gate（人間判断）

特に、次の原則を実演します。

1. **AI出力は自動的に正本にならない。**
2. 新しい正本候補を作成しても、旧正本を削除・上書きしない。
3. 現行正本は `05_CANONICAL/CANONICAL_POINTER.yaml` からのみ解決する。
4. 未解消のHOLDは、無理にPASSへ変更せず残す。
5. 正本切替と公開可否は、AIではなくHuman Gateの専権事項とする。

## 架空施工例

仮想道路改良工事において、下層路盤施工前の路床施工基面を確認します。

現場記録では、1測点で暫定許容差を外れ、同地点付近に局所的な軟弱箇所が確認されています。ただし、その平面範囲と深さは未確認です。

このため、

- 原証憑は `02_EVIDENCE/` に保存
- 出来形照査結果は `03_INSPECTION/` に分離
- 未確認事項は `04_HOLD/` に保持
- 現行正本 `BASELINE_V1.yaml` は維持
- 是正条件を追加した `BASELINE_V2.yaml` は**正本候補**としてのみ作成
- `CANONICAL_POINTER.yaml` はHuman Gate承認までV1を指し続ける

という施工管理を行っています。

## 公開境界

- 実案件情報は含みません。
- 個人情報、資格情報、private URL、秘密情報を意図的に含みません。
- 未公開の特許関連資料・内部研究成果は含みません。
- 本束は現在 **PRIVATE STAGING** です。
- public repositoryへの搬出は未承認です。
- `HUMAN_GATE.yaml` の `public_release.state` は **HOLD** のままです。

---

# English Reference Translation

> **The Japanese section above is authoritative. This English section is provided for reference only.**

This directory contains a **synthetic civil-construction example** prepared for human inspection before any public release. No real project data is used.

## Purpose

The exemplar demonstrates separation of:

- work order,
- source evidence,
- inspection,
- HOLD items,
- current canonical baseline,
- candidate baseline,
- change history, and
- Human Gate decisions.

The example is designed to show that:

1. **AI output does not automatically become canonical.**
2. An existing canonical baseline is preserved when a new candidate is created.
3. `05_CANONICAL/CANONICAL_POINTER.yaml` is the sole resolver for the current canonical baseline.
4. Unresolved HOLD items remain open instead of being forced to PASS.
5. Canonical change and public release remain Human Gate decisions.

## Synthetic Example

A fictional road-improvement work section is inspected before lower-base-course placement.

Field evidence records one formation-level result outside the provisional tolerance and a localized soft spot. The horizontal extent and depth of the soft spot remain unconfirmed.

Accordingly:

- source evidence is stored under `02_EVIDENCE/`;
- inspection results are separated under `03_INSPECTION/`;
- unresolved matters remain under `04_HOLD/`;
- `BASELINE_V1.yaml` remains the current canonical baseline;
- `BASELINE_V2.yaml` is created only as a candidate containing proposed corrective conditions; and
- `CANONICAL_POINTER.yaml` continues to resolve V1 until Human Gate approval.

## Release Boundary

- No real project data is included.
- No personal data, credentials, private URLs, or secrets are intentionally included.
- No unpublished patent-sensitive material or internal research output is included.
- This bundle remains in **PRIVATE STAGING**.
- Transfer to a public repository has not been authorized.
- `HUMAN_GATE.yaml` keeps `public_release.state` at **HOLD**.
