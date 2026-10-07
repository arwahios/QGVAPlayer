//
//  QGVAPlayerView.m
//  QGVAPlayer
//
//  Created by Arwah on 2026/10/07.
//

#import "QGVAPlayer.h"
#import "UIView+VAP.h"

@interface QGVAPlayerView () <HWDMP4PlayDelegate>
@property (nonatomic, copy) NSDictionary<NSString *, NSString *> *tagContents;
@property (nonatomic, copy, nullable) QGVAFinishedBlock onFinished;
@property (nonatomic, copy, nullable) QGVAFailedBlock onFailed;
@property (nonatomic, assign) BOOL didEnd;
@property (nonatomic, copy, nullable) NSString *playingPath;
@end

@implementation QGVAPlayerView

- (instancetype)initWithFrame:(CGRect)frame {
    self = [super initWithFrame:frame];
    if (self) {
        self.backgroundColor = UIColor.clearColor;
        self.userInteractionEnabled = NO;
        self.hwd_enterBackgroundOP = HWDMP4EBOperationTypeStop;
        [self enableOldVersion:YES];
        [self setMute:YES];
    }
    return self;
}

- (void)playFileAtPath:(NSString *)path
           tagContents:(NSDictionary<NSString *, NSString *> *)tagContents
            onFinished:(QGVAFinishedBlock)onFinished
              onFailed:(QGVAFailedBlock)onFailed {
    if (path.length == 0) {
        if (onFailed) {
            onFailed([NSError errorWithDomain:@"QGVAPlayer" code:-1 userInfo:@{NSLocalizedDescriptionKey: @"empty path"}]);
        }
        return;
    }
    self.tagContents = tagContents ?: @{};
    self.onFinished = onFinished;
    self.onFailed = onFailed;
    self.didEnd = NO;
    self.playingPath = path;
    [self playHWDMP4:path repeatCount:0 delegate:self];
}

- (void)stopPlayback {
    [self stopHWDMP4];
}

#pragma mark - HWDMP4PlayDelegate

- (NSString *)contentForVapTag:(NSString *)tag resource:(QGVAPSourceInfo *)info {
    NSString *key = tag ?: @"";
    NSString *value = self.tagContents[key];
    if (value) { return value; }
    NSString *stripped = [key stringByTrimmingCharactersInSet:[NSCharacterSet characterSetWithCharactersInString:@"[]"]];
    value = self.tagContents[stripped];
    return value ?: tag;
}

- (void)loadVapImageWithURL:(NSString *)urlStr
                    context:(NSDictionary *)context
                 completion:(VAPImageCompletionBlock)completionBlock {
    if (urlStr.length == 0 || !completionBlock) {
        if (completionBlock) {
            completionBlock(nil, [NSError errorWithDomain:NSURLErrorDomain code:NSURLErrorBadURL userInfo:nil], urlStr);
        }
        return;
    }
    NSURL *url = [NSURL URLWithString:urlStr];
    if (!url) {
        completionBlock(nil, [NSError errorWithDomain:NSURLErrorDomain code:NSURLErrorBadURL userInfo:nil], urlStr);
        return;
    }
    NSURLSessionDataTask *task = [[NSURLSession sharedSession] dataTaskWithURL:url
                                                             completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
        UIImage *image = data ? [UIImage imageWithData:data] : nil;
        dispatch_async(dispatch_get_main_queue(), ^{
            completionBlock(image, error, urlStr);
        });
    }];
    [task resume];
}

- (void)endOnceWithFinished:(BOOL)finished error:(NSError *)error {
    if (self.didEnd) { return; }
    self.didEnd = YES;
    dispatch_async(dispatch_get_main_queue(), ^{
        if (error && self.onFailed) {
            self.onFailed(error);
        } else if (self.onFinished) {
            self.onFinished();
        }
    });
}

- (void)viewDidFinishPlayMP4:(NSInteger)totalFrameCount view:(UIView *)container {
    [self endOnceWithFinished:YES error:nil];
}

- (void)viewDidStopPlayMP4:(NSInteger)lastFrameIndex view:(UIView *)container {
    [self endOnceWithFinished:YES error:nil];
}

- (void)viewDidFailPlayMP4:(NSError *)error {
    [self endOnceWithFinished:NO error:(error ?: [NSError errorWithDomain:@"QGVAPlayer" code:-2 userInfo:nil])];
}

@end
