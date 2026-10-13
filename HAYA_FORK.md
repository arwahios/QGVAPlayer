# Haya QGVAPlayer

- Upstream: [Tencent/vap](https://github.com/Tencent/vap) tag `iOS1.0.19`（开源仓已停止维护，仍可用于现有 `.mp4` VAP 物料）
- 接入方式：SPM；产物为 **动态 framework**（`type: .dynamic`），便于宿主 Embed 后与 Flutter 共用同一份运行时；**禁止** App Podfile `post_install` 改源码
- App Target → Frameworks, Libraries, and Embedded Content：对 `QGVAPlayer` 选 **Embed & Sign**（经 EffectKit 传递依赖时若未自动出现，在 App 上再显式链一次）
- 安全补丁已直接打进源码（对齐现网必要项，标记 `Haya:`）：
  - skip `MTKTextureLoader`
  - YCbCr attachment 空指针保护
  - Metal dispose / stop 释放与线程安全
  - 小尺寸 drawable scale 限制
- Feature 只依赖 EffectKit；换播放器只改 Adapter
- `QGVAPlayerView` 默认 `setMute:NO`（礼物音效）；`setMuted:` 须在 play 前调用

推远程示例：

```bash
git tag 1.0.19-haya.3
git push origin main 1.0.19-haya.3
```
