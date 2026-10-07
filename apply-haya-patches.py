#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "Sources/QGVAPlayer"


def patch(rel: str, old: str, new: str, label: str) -> None:
    path = ROOT / rel
    text = path.read_text()
    if "Haya:" in new and new.split("Haya:", 1)[1][:24].strip() in text:
        print("SKIP", label)
        return
    if old not in text:
        print("FAIL", label)
        return
    path.write_text(text.replace(old, new, 1))
    print("OK", label)


patch(
    "Classes/Models/QGVAPTextureLoader.m",
    """    if (@available(iOS 10.0, *)) {
        MTKTextureLoader *loader = [[MTKTextureLoader alloc] initWithDevice:device];
        NSError *error = nil;
        id<MTLTexture> texture = [loader newTextureWithCGImage:image.CGImage options:@{MTKTextureLoaderOptionOrigin : MTKTextureLoaderOriginFlippedVertically,MTKTextureLoaderOptionSRGB:@(NO)} error:&error];
        if (!texture || error) {
            VAP_Error(kQGVAPModuleCommon, @"loadTexture error:%@", error);
            return nil;
        }
        return texture;
    }
    return [self cg_loadTextureWithImage:image device:device];""",
    """    // Haya: skip MTKTextureLoader — ImageIO backend objects linger under gift load.
    return [self cg_loadTextureWithImage:image device:device];""",
    "TextureLoader skip MTK",
)

for rel in (
    "Classes/Views/Metal/QGHWDMetalRenderer.m",
    "Classes/Views/Metal/Vapx/QGVAPMetalRenderer.m",
):
    patch(
        rel,
        """    CFTypeRef yCbCrMatrixType = CVBufferGetAttachment(pixelBuffer, kCVImageBufferYCbCrMatrixKey, NULL);
    matrix_float3x3 matrix = kQGColorConversionMatrix601FullRangeDefault;
    if (CFStringCompare(yCbCrMatrixType, kCVImageBufferYCbCrMatrix_ITU_R_709_2, 0) == kCFCompareEqualTo) {
        matrix = kQGColorConversionMatrix709FullRangeDefault;
    }""",
        """    CFTypeRef yCbCrMatrixType = CVBufferGetAttachment(pixelBuffer, kCVImageBufferYCbCrMatrixKey, NULL);
    matrix_float3x3 matrix = kQGColorConversionMatrix601FullRangeDefault;
    // Haya: yCbCr null-check
    if (yCbCrMatrixType && CFGetTypeID(yCbCrMatrixType) == CFStringGetTypeID()
        && CFStringCompare((CFStringRef)yCbCrMatrixType, kCVImageBufferYCbCrMatrix_ITU_R_709_2, 0) == kCFCompareEqualTo) {
        matrix = kQGColorConversionMatrix709FullRangeDefault;
    }""",
        f"{rel} yCbCr",
    )

patch(
    "Classes/Views/Metal/Vapx/QGVAPMetalRenderer.m",
    """- (void)dispose {
    
    _commandQueue = nil;
    _vertexBuffer = nil;
    _yuvMatrixBuffer = nil;
    _attachmentPipelineState = nil;
    _shaderFuncLoader = nil;
    if (_videoTextureCache) {
        CVMetalTextureCacheFlush(_videoTextureCache, 0);
        CFRelease(_videoTextureCache);
        _videoTextureCache = NULL;
    }
    _renderingResourcesDisposed = YES;
    _mainPipelineStateForMask = nil;
    _defaultMainPipelineState = nil;
}""",
    """- (void)dispose {
    
    _commandQueue = nil;
    _vertexBuffer = nil;
    _yuvMatrixBuffer = nil;
    _maskBlurBuffer = nil;
    _attachmentPipelineState = nil;
    _shaderFuncLoader = nil;
    if (_videoTextureCache) {
        CVMetalTextureCacheFlush(_videoTextureCache, 0);
        CFRelease(_videoTextureCache);
        _videoTextureCache = NULL;
    }
    _renderingResourcesDisposed = YES;
    _mainPipelineStateForMask = nil;
    _mainPipelineStateForMaskBlur = nil;
    _defaultMainPipelineState = nil;
}""",
    "QGVAPMetalRenderer dispose",
)

vap = ROOT / "Classes/UIView+VAP.m"
text = vap.read_text()

replacements = [
    (
        """//结束播放
- (void)hwd_stopHWDMP4 {
    
    VAP_Info(kQGVAPModuleCommon, @"hwd stop playing");
    self.hwd_repeatCount = 0;
    if (self.hwd_isFinish) {
        VAP_Info(kQGVAPModuleCommon, @"isFinish already set");
        return ;
    }
    self.hwd_isFinish = YES;
    self.hwd_onPause = YES;
    if (self.hwd_openGLView) {
         self.hwd_openGLView.pause = YES;
        if ([EAGLContext currentContext] != self.hwd_openGLView.glContext) {
            [EAGLContext setCurrentContext:self.hwd_openGLView.glContext];
        }
        [self.hwd_openGLView dispose];
        glFinish();
    }
    if (self.hwd_metalView) {
        [self.hwd_metalView dispose];
    }
    if (self.vap_metalView) {
        [self.vap_metalView dispose];
    }
    [self.hwd_decodeManager tryToStopAudioPlay];""",
        """//结束播放
- (void)hwd_stopHWDMP4 {
    // Haya: stop-on-main
    if (![NSThread isMainThread]) {
        dispatch_async(dispatch_get_main_queue(), ^{
            [self hwd_stopHWDMP4];
        });
        return;
    }
    VAP_Info(kQGVAPModuleCommon, @"hwd stop playing");
    self.hwd_repeatCount = 0;
    if (self.hwd_isFinish) {
        VAP_Info(kQGVAPModuleCommon, @"isFinish already set");
        return ;
    }
    self.hwd_isFinish = YES;
    self.hwd_onPause = YES;
    // Haya: stop lock around dispose
    @synchronized (self) {
    if (self.hwd_openGLView) {
         self.hwd_openGLView.pause = YES;
        if ([EAGLContext currentContext] != self.hwd_openGLView.glContext) {
            [EAGLContext setCurrentContext:self.hwd_openGLView.glContext];
        }
        [self.hwd_openGLView dispose];
        glFinish();
        [self.hwd_openGLView removeFromSuperview];
        self.hwd_openGLView = nil;
    }
    // Haya: release metal views after stop
    if (self.hwd_metalView) {
        [self.hwd_metalView dispose];
        [self.hwd_metalView removeFromSuperview];
        self.hwd_metalView = nil;
    }
    if (self.vap_metalView) {
        [self.vap_metalView dispose];
        [self.vap_metalView removeFromSuperview];
        self.vap_metalView = nil;
    }
    // Haya: drop attachment MTLTextures held by config
    self.hwd_configManager = nil;
    }
    [self.hwd_decodeManager tryToStopAudioPlay];""",
        "UIView stop",
    ),
    (
        """//播放完成
- (void)hwd_didFinishDisplay {
    
    VAP_Info(kQGVAPModuleCommon, @"hwd didFinishDisplay");""",
        """//播放完成
- (void)hwd_didFinishDisplay {
    if (![NSThread isMainThread]) {
        // Haya: finish-display bounce to main
        BOOL willLoop = (self.hwd_repeatCount == -1 || self.hwd_repeatCount > 0);
        if (willLoop) {
            dispatch_sync(dispatch_get_main_queue(), ^{
                [self hwd_didFinishDisplay];
            });
        } else {
            dispatch_async(dispatch_get_main_queue(), ^{
                [self hwd_didFinishDisplay];
            });
        }
        return;
    }
    if (self.hwd_isFinish) {
        return;
    }
    VAP_Info(kQGVAPModuleCommon, @"hwd didFinishDisplay");""",
        "UIView finish",
    ),
    (
        """    VAP_Info(kQGVAPModuleCommon, @"try to display mp4:%@ blendMode:%@ fps:%@ repeatCount:%@", filePath, @(mode), @(fps), @(repeatCount));
    NSAssert([NSThread isMainThread], @"HWDMP4 needs to be accessed on the main thread.");
    //filePath check""",
        """    VAP_Info(kQGVAPModuleCommon, @"try to display mp4:%@ blendMode:%@ fps:%@ repeatCount:%@", filePath, @(mode), @(fps), @(repeatCount));
    NSAssert([NSThread isMainThread], @"HWDMP4 needs to be accessed on the main thread.");
    // Haya: stop only when switching to a different mp4
    if (!self.hwd_isFinish && self.hwd_fileInfo.filePath.length > 0 && ![self.hwd_fileInfo.filePath isEqualToString:filePath]) {
        [self hwd_stopHWDMP4];
    }
    //filePath check""",
        "UIView play stop",
    ),
    (
        """    self.hwd_isFinish = NO;
    self.hwd_blendMode = mode;
    self.hwd_fps = fps;
    self.hwd_repeatCount = repeatCount;""",
        """    self.hwd_isFinish = NO;
    self.hwd_blendMode = mode;
    // Haya: fps<=0 keep preset hwd_fps
    if (fps >= kQGHWDMP4MinFPS && fps <= QGHWDMP4MaxFPS) {
        self.hwd_fps = fps;
    }
    self.hwd_repeatCount = repeatCount;""",
        "UIView fps",
    ),
    (
        """                __block QGMP4AnimatedImageFrame *nextFrame = nil;
                dispatch_sync(dispatch_get_main_queue(), ^{
                    nextFrame = [self hwd_displayNext];
                });""",
        """                __block QGMP4AnimatedImageFrame *nextFrame = nil;
                if (self.hwd_renderByOpenGL) {
                    dispatch_sync(dispatch_get_main_queue(), ^{
                        nextFrame = [self hwd_displayNext];
                    });
                } else {
                    // Haya: Metal on vap_renderQueue
                    nextFrame = [self hwd_displayNext];
                }""",
        "UIView render loop",
    ),
    (
        """    nextFrame.duration = [self hwd_appropriateDurationForFrame:nextFrame];
    //VAP_Debug(kQGVAPModuleCommon, @"display frame:%@, has frameBuffer:%@",@(nextIndex),@(nextFrame.pixelBuffer != nil));
    if (self.hwd_renderByOpenGL) {
        [self.hwd_openGLView displayPixelBuffer:nextFrame.pixelBuffer];
    } else if (self.useVapMetalView) {
        NSArray<QGVAPMergedInfo *> *mergeInfos = self.hwd_configManager.model.mergedConfig[@(nextFrame.frameIndex)];
        [self.vap_metalView display:nextFrame.pixelBuffer mergeInfos:mergeInfos];
    } else {
        [self.hwd_metalView display:nextFrame.pixelBuffer];
    }""",
        """    nextFrame.duration = [self hwd_appropriateDurationForFrame:nextFrame];
    //VAP_Debug(kQGVAPModuleCommon, @"display frame:%@, has frameBuffer:%@",@(nextIndex),@(nextFrame.pixelBuffer != nil));
    // Haya: serialize metal submit vs stop
    @synchronized (self) {
        if (self.hwd_onPause || self.hwd_isFinish) {
            return nil;
        }
        if (self.hwd_renderByOpenGL) {
            [self.hwd_openGLView displayPixelBuffer:nextFrame.pixelBuffer];
        } else if (self.useVapMetalView) {
            NSArray<QGVAPMergedInfo *> *mergeInfos = self.hwd_configManager.model.mergedConfig[@(nextFrame.frameIndex)];
            [self.vap_metalView display:nextFrame.pixelBuffer mergeInfos:mergeInfos];
        } else {
            [self.hwd_metalView display:nextFrame.pixelBuffer];
        }
    }""",
        "UIView submit",
    ),
]

for old, new, label in replacements:
    if old not in text:
        print("FAIL", label)
        continue
    text = text.replace(old, new, 1)
    print("OK", label)
vap.write_text(text)

for rel in (
    "Classes/Views/Metal/QGHWDMetalView.m",
    "Classes/Views/Metal/Vapx/QGVAPMetalView.m",
):
    p = ROOT / rel
    t = p.read_text()
    old_w = """    if (!self.window) {
        VAP_Event(kQGVAPModuleCommon, @"quit display pixelbuffer, cuz window is nil!");
        [self onMetalViewUnavailable];
        return ;
    }
    if (self.drawableSizeShouldUpdate) {
        CGFloat nativeScale = [UIScreen mainScreen].nativeScale;
        CGSize drawableSize = CGSizeMake(CGRectGetWidth(self.bounds)*nativeScale, CGRectGetHeight(self.bounds)*nativeScale);
        self.metalLayer.drawableSize = drawableSize;
        VAP_Event(kQGVAPModuleCommon, @"update drawablesize :%@", [NSValue valueWithCGSize:drawableSize]);
        self.drawableSizeShouldUpdate = NO;
    }"""
    new_w = """    if (!self.metalLayer.superlayer) {
        VAP_Event(kQGVAPModuleCommon, @"quit display pixelbuffer, cuz metalLayer is detached!");
        [self onMetalViewUnavailable];
        return ;
    }
    if (self.drawableSizeShouldUpdate) {
        CGFloat nativeScale = [UIScreen mainScreen].nativeScale;
        // Haya: small decorative VAP drawable scale cap
        CGRect layerBounds = self.metalLayer.bounds;
        CGFloat maxSide = MAX(CGRectGetWidth(layerBounds), CGRectGetHeight(layerBounds));
        if (maxSide > 0 && maxSide <= 200.0) {
            nativeScale = MIN(nativeScale, 2.0);
        }
        CGSize drawableSize = CGSizeMake(CGRectGetWidth(layerBounds)*nativeScale, CGRectGetHeight(layerBounds)*nativeScale);
        self.metalLayer.drawableSize = drawableSize;
        VAP_Event(kQGVAPModuleCommon, @"update drawablesize :%@", [NSValue valueWithCGSize:drawableSize]);
        self.drawableSizeShouldUpdate = NO;
    }"""
    if old_w in t:
        t = t.replace(old_w, new_w, 1)
        print("OK drawable", rel)
    else:
        print("FAIL drawable", rel)

    old_u = """- (void)onMetalViewUnavailable{
    
    if ([self.delegate respondsToSelector:@selector(onMetalViewUnavailable)]) {
        [self.delegate onMetalViewUnavailable];
    }
}"""
    new_u = """- (void)onMetalViewUnavailable{
    // Haya: onMetalViewUnavailable bounce to main
    if (![NSThread isMainThread]) {
        dispatch_async(dispatch_get_main_queue(), ^{
            [self onMetalViewUnavailable];
        });
        return;
    }
    if ([self.delegate respondsToSelector:@selector(onMetalViewUnavailable)]) {
        [self.delegate onMetalViewUnavailable];
    }
}"""
    if old_u in t:
        t = t.replace(old_u, new_u, 1)
        print("OK unavailable", rel)
    else:
        print("FAIL unavailable", rel)
    p.write_text(t)

print("done")
