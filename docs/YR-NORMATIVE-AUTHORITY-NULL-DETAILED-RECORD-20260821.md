# なぜ規範的最終権限はNULLで設計するのか（詳細版）

## 目的

本記録は、YamRail関連技術報告および監査過程で形成された「Normative Authority_AI = NULL」の設計理由を、証憑・判断境界・由来管理の観点から整理する。

## 基本命題

AIを高性能化しても、AI内部の可変な意味状態へ規範的最終権限を恒久割当してはならない。

理由は、情報の到達性・反復・再構成能力が、そのまま真理性や正当性を保証しないためである。

## 確認された構造

- Reachability と Validity は別軸
- Citation Presence と Source Validity は別軸
- Model Consensus と Normative Authority は別軸
- Human Authority と Human Infallibility は別軸

## 設計帰結

Human Gateは真理そのものではなく権限境界である。
AIは施工能力を持つが、規範的最終裁定主体にはしない。

## 監査で確認された重要事項

- 引用存在と引用支持は分離する必要がある
- 由来記録が失われた場合、内容が正しくても証憑閉包は成立しない
- HOLDは失敗ではなく未閉包状態を保持する安全状態である

## 最終原則

Evidence must be reachable to be useful, but reachability must never be treated as evidence of truth.

Neither human nor AI fallibility should be allowed to become an uninspected system authority.

Normative Authority_AI = NULL
