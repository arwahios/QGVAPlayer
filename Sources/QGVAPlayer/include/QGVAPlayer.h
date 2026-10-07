//
//  QGVAPlayer.h
//  QGVAPlayer
//
//  Created by Arwah on 2026/10/07.
//
//  Thin public facade for SPM / Swift. Implementation uses UIView+VAP privately.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

typedef void (^QGVAFinishedBlock)(void);
typedef void (^QGVAFailedBlock)(NSError *error);

/// Full-screen / gift VAP host. Feature code should go through EffectKit, not this type.
@interface QGVAPlayerView : UIView

/// `tagContents`: VAP fusion tag → text or image URL string.
- (void)playFileAtPath:(NSString *)path
           tagContents:(NSDictionary<NSString *, NSString *> *)tagContents
            onFinished:(nullable QGVAFinishedBlock)onFinished
              onFailed:(nullable QGVAFailedBlock)onFailed;

- (void)stopPlayback;

@end

NS_ASSUME_NONNULL_END
