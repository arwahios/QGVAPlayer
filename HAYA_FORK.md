# Haya QGVAPlayer

- Upstream: [Tencent/vap](https://github.com/Tencent/vap) tag `iOS1.0.19`（开源仓已停止维护，仍可用于现有 `.mp4` VAP 物料）
- 接入方式：SPM；**禁止** App Podfile `post_install` 改源码
- 安全补丁已直接打进源码（对齐现网必要项，标记 `Haya:`）：
  - skip `MTKTextureLoader`
  - YCbCr attachment 空指针保护
  - Metal dispose / stop 释放与线程安全
  - 小尺寸 drawable scale 限制
- Feature 只依赖 EffectKit；换播放器只改 Adapter

推远程示例：

```bash
# 在 arwahios 下新建空仓 QGVAPlayer 后：
cd Packages/ThirdParty/QGVAPlayer
git init
git add .
git commit -m "chore: QGVAPlayer iOS1.0.19 + Haya safety patches"
git remote add origin git@github.com:arwahios/QGVAPlayer.git
git push -u origin main
git tag 1.0.19-haya.1
git push origin 1.0.19-haya.1
```
