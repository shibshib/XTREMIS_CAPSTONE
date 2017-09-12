addpath('eeglab');
%eeglab;

IN_FILE = 'Data/compare/fisting_s1';
Fs = 1024;

xt_data = csvread([IN_FILE '_conv.TXT']);
bs_data = pop_biosig([IN_FILE '.bdf']);
bs_data = pop_resample(bs_data, 1024);

xt_data = xt_data.';

% drop sample # channel
xt_data = xt_data(2:9, :);

bpFilt = designfilt('bandpassfir', 'FilterOrder', 20, 'CutOffFrequency1', 7, 'CutoffFrequency2', 13,'SampleRate', 1024);

notch = designfilt('bandstopfir', 'FilterOrder', 20, 'CutoffFrequency1', 55, 'CutoffFrequency2', 65, 'SampleRate', 1024);

% loop through channels
corrs = zeros(8, 1);

for i=1:8

    xt = xt_data(i, :);
    bs = bs_data.data(i, :);
    
    % reference
    bs = bs - mean(bs_data.data);
    xt = xt - mean(xt_data);
    
    % remove any large spikes in data
    bs = bs(find(abs(zscore(bs)) < 1.5));
    xt = xt(find(abs(zscore(xt)) < 1.5));
    
    % filter
    bs = filter(bpFilt, bs);
    bs = filter(notch, bs);
    xt = filter(bpFilt, xt);
    xt = filter(notch, xt);


    % make signals the same length
    lbs = length(bs);
    lxt = length(xt);
    if lxt > lbs
        xt = xt(lxt-lbs+1:end);
    else
        bs = bs(lbs-lxt+1:end);
    end;

    % look at middle 75% of data
    lo = int32(0.125 * length(bs));
    hi = int32(0.875 * length(bs));

    %disp(['looking at ' num2str((hi - lo)/1024) ' seconds of data']);

    bs = bs(lo:hi);
    xt = xt(lo:hi);
    
    % remove mean and normalize
    xt = xt - mean(xt);
    xt = xt / max(abs(xt));
    
    bs = bs - mean(bs);
    bs = bs / max(abs(bs));

    % do xcorr
    [r, lags] = xcorr(bs, xt, 'coeff');
    corrs(i) = max(r);
    
end;

corrs
disp(['mean:' num2str(mean(corrs))]);
disp(['std:' num2str(std(corrs))]);

% plot channels with psd
figure;
subplot(2,2,1);
plot(xt);
title('Xtremis Data');

N = length(xt);
xdft = fft(xt);
xdft = xdft(1:N/2+1);
psdx1 = (1/(Fs*N)) * abs(xdft).^2;
psdx1(2:end-1) = 2*psdx1(2:end-1);
freq = 0:Fs/length(xt):Fs/2;

subplot(2,2,2)
plot(freq,10*log10(psdx1))
grid on
title('Xtremis PSD')
xlabel('Frequency (Hz)')
ylabel('Power/Frequency (dB/Hz)')
ylim([-130 0])



subplot(2,2,3);
plot(bs);
title('Biosemi Data');

N = length(bs);
xdft = fft(bs);
xdft = xdft(1:N/2+1);
psdx = (1/(Fs*N)) * abs(xdft).^2;
psdx(2:end-1) = 2*psdx(2:end-1);
freq = 0:Fs/length(bs):Fs/2;

subplot(2,2,4)
plot(freq,10*log10(psdx))
grid on
title('Biosemi PSD')
xlabel('Frequency (Hz)')
ylabel('Power/Frequency (dB/Hz)')
ylim([-130 0])
