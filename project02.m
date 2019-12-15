clear;clc
arriving_rate = 0.1:0.001:4.9;
serving_rate = 1;
opt_values = zeros(1, length(arriving_rate));
opt_ss = zeros(1, length(arriving_rate));
x = -2:2;
x = 2.^x;
name = [];
for i = 1:length(x)
    for j=1:length(arriving_rate)
        [opt_values(j), opt_ss(j)] = optimize_num(arriving_rate(j), serving_rate, 10, x(i));
    end
    plot(arriving_rate, opt_ss)
    name = [name; string("x="+x(i))];
    hold on
end
legend(name)

function [opt_v, opt_s] = optimize_num(arrv, serv, s_max, x)
    a = arrv ./ serv;
    s = 0:s_max-1;
    sum_s = a.^(s - s_max) ./ factorial(s);
    sum_s = cumsum(sum_s);
    s = ceil(a):s_max;
    x_s = (s-a).^2 .* factorial(s-1) .* sum_s(s) + s - a;
    W = 1 ./ serv .* (1 + 1 ./ x_s);
    C = x.*(s+1);
    L = W + C;
    [opt_v, opt_s] = min(L);
    opt_s = opt_s + ceil(a) - 1;
end
