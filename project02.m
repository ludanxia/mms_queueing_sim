clear;clc
arriving_rate = 0.1:0.01:4.9;
serving_rate = 1;
opt_values = zeros(1, length(arriving_rate));
opt_ss = zeros(1, length(arriving_rate));
opt_w = zeros(1, length(arriving_rate));
opt_c = zeros(1, length(arriving_rate));
theta = [0, 1, 2];
x = [30, 40, 50]/60;
name = [];
for i = 1:length(theta)
    for j = 1:length(x)
        for k=1:length(arriving_rate)
            [opt_values(k), opt_ss(k), opt_w(k), opt_c(k)] = optimize_num(arriving_rate(k), serving_rate, 10, x(j), theta(i));
        end
        plot(arriving_rate, opt_ss)
        hold on
        name = [name; string("x="+x(j)+", \theta ="+theta(i))];
    end
end
xlabel("\lambda / \mu")
ylabel("r_{opt}")
legend(name, 'location', 'bestoutside')

function [opt_v, opt_s, opt_W, opt_C] = optimize_num(arrv, serv, s_max, x, theta)
    a = arrv ./ serv;
    s = 0:s_max-1;
    sum_s = a.^(s - s_max) ./ factorial(s);
    sum_s = cumsum(sum_s);
    s = ceil(a):s_max;
    x_s = (s-a).^2 .* factorial(s-1) .* sum_s(s) + s - a;
    W = 1 ./ serv .* (1 + 1 ./ x_s);
    C = x.* s;
    L = W + theta * C;
    [opt_v, opt_s] = min(L);
    opt_W = W(opt_s);
    opt_C = C(opt_s);
    opt_s = opt_s + ceil(a) - 1;
end
