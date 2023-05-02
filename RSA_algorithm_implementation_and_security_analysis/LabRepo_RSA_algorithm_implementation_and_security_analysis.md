---
title: RSA算法优化实现和安全性分析
keywords: [RSA, 素性检测, 公共模攻击, 不动点攻击]
date: 2023.05.03
---

# 一、实验目的

通过本次实验，完成下列目标：

- 使用大数库实现200比特以上长度模数RSA
- 为素性检测、RSA算法编写独立模块
- 100比特以上大素数p、q通过素性检测算法自行生成
- 测试RSA算法的执行效率（对单个明文数据执行万次以上求时间平均值）
- RSA算法优化实现，提高加解密速度。优化方法包括模指数运算，二进制欧几里得算法，二进制扩展欧几里得算法，利用孙子定理提高解密速度等。

# 二、实验原理

## 1. RSA算法介绍

### 1.1 RSA算法简介

RSA公开密钥密码体制是一种使用不同的加密密钥与解密密钥。在公开密钥密码体制中，加密密钥PK是公开信息，而解密密钥SK是需要保密的。加密算法E和解密算法D也都是公开的。虽然解密密钥SK是由公开密钥PK决定的，但却不能根据PK计算出SK。

而RSA的安全性就依赖于大数分解。根据数论，寻求两个大素数比较简单，而将它们的乘积进行因式分解却极其困难，因此可以将乘积公开作为加密密钥的一部分。

### 1.2 RSA算法流程

#### 1.2.1 密钥生成

1. 任意选取两个不同的大素数$p$和$q$计算 $n=pq,\phi(n)=(p-1)(q-1)$
2. 任意选取一个较大的数$e$且满足$1<e<\phi(n),gcd(e,\phi(n))=1$
3. 计算$e$模$\phi(n)$的逆元$d$，即$d$满足$ed\equiv1(mod\phi(n)),1<d<\phi(n)$

由此得到了一个密钥对：

- 公开密钥$n$和$e$（加密指数）
- 私有密钥$d$（解密指数）

#### 1.2.2 RSA加密

对于明文$x$，用公钥$(n, e)$对$x$加密的过程，就是将$x$转换成数字（字符串的话取其 ASCII 码或者 Unicode 值），然后通过幂取模计算出$y$，其中$y$就是密文：

$$
y\equiv x^{e} \bmod n
$$

#### 1.2.3 RSA解密

对于密文$y$，用私钥$(n, d)$对$y$进行解密的过程和加密类似，同样是计算幂取模：

$$
x\equiv y^{d} \bmod n
$$

正确性可以简证如下：

$$
y^{d} \equiv (x^{e})^{d} = x^{ed} \equiv x \bmod n
$$

### 1.3 素性检测

在上面的流程中，我们发现产生一对大的“随机素数”是必不可少的，而一些确定性的素性检测算法或素数生成算法在大整数下的效率又太低，因此需要检测大整数是否是素数的概率算法，在这里我们使用*Miller-Rabin*素性检测算法，这是一个“判定一个奇整数是否为合数”的偏是*Monte Carlo*算法，错误概率为$1/4$，算法流程如下：

首先选取一个待测的随机数$n$，求取$k$和$m$使得$n-1=2^km$且$2\not\mid m$

1. 选取一个随机数$a$，使得$1\le a \le n-1$
2. 计算$b\equiv a^m \bmod n$
3. 如果$b\equiv1\bmod n$，则回答“$n$是素数”并退出
4. 否则，对于$i=0,\cdots,k-1$，执行如下步骤：
   1. 如果$b\equiv-1\bmod n$，则回答“$n$是素数”并退出
   2. 否则令$b\leftarrow b^2\bmod n$
5. 回答“$n$是合数”并退出

### 1.4 RSA安全性分析

而对于外界来说，知道的只有公钥$(n, e)$，如何通过这两个已知数得到明文?
- 1) 首先，明文需要密文的$d$次幂模上$n$来计算，所以首先要知道$d$;
- 2)  $d$为$e$对$\phi(n)$的逆元，如果知道$\phi(n)$，则能够通过扩展欧几里德算法计算出$d$；
- 3)  $\phi(n)=(p-1)(q-1)$，其中$p$和$q$均为素数，只有得知$p$和$q$的值才能计算出$\phi(n)$;
- 4)  $n=pq$，$n$已知，所以如果能够分解$n$，则$p$和$q$就能被计算出来。

因此最朴素的方法就是大数分解，而RSA的安全性就是依赖于大数分解。针对RSA的攻击很多，但都没有对它构成真正的威胁，下面列举了部分对于RSA的典型攻击方法。

#### 1.4.1 选择密码攻击

RSA在选择密码攻击面前显得很脆弱。一般攻击者是将某一信息进行下伪装，让拥有私钥的实体签名；然后，经过计算就可得到它所想要的信息。实际上，攻击利用的都是同一个弱点，即存在这样一个事实：乘幂保留了输入的乘法结构。从算法上无法解决这一问题，改进措施有两条：是采用好的公钥协议保证工作过程中实体不对其他实体任意产生的信息解密，不对自己一无所知的信息签名；二是决不对陌生人送来的随机文档签名，或签名时首先对文档作Hash处理，或同时使用不同的签名算法。

#### 1.4.2 小指数攻击

当公钥$e$取较小的值，虽然会使加密变得易于实现，速度有所提高，但这样做也是不安全的。最简单的办法就是$e$和$d$都取较大的值。

#### 1.4.3 公共模攻击

生成秘钥的过程中使用了相同的模数$n$，此时用不同的秘钥$e_1,e_2$加密同一信息$m$即：

$$
c_1 = m^{e_1} % n
c_2 = m^{e_2} % n
$$

若两个秘钥$e_1,e_2$互素，则存在$s_1,s_2$有：

$$
e_1 * s_1 + e_2 * s_2 = gcd(e_1, e_2) = 1
$$

结合以上所有信息，可以得到一个结论：

$$
(c_1^{s_1} * c_2^{s_2})
\equiv  (m^{e_1})^{s_1} * (m^{e_2})^{s_2}
\equiv  m^{(e_1 * s_1 + e_2 * s_2)}
\equiv  m \bmod n
$$

也就是在完全不知道私钥的情况下，得到了明文$m$

$$
m \equiv (c_1^{s_1} * c_2^{s_2}) \bmod n
$$

#### 1.4.4 不动点攻击

称满足$m^e\equiv m \bmod n$的$m$称为不动点，显然不动点对RSA的安全性有一定威胁，因此要尽量减少不动点个数。可以证明RSA体制下的不动点个数为
$$
[gcd(e-1,p-1)+1]\times[gcd(e-1,q-1)+1]
$$
由此，为了减少不动点个数，必须使$p-1$和$q-1$的因子尽可能少。*如果$a$是素数，则称素数$p=2a+1$为安全素数*，因此当$p$和$q$为安全素数使，不动点个数达到最小值9个。

# 三、实验内容

## 1. 概率素性检测

根据*Miller-Rabin*算法原理，编写如下代码：

```python
def miller_rabin(test_num: int) -> bool:
    if test_num < 2:
        return False
    m = test_num - 1
    k = 0
    while not (m & 1):
        k = k + 1
        m = m >> 1
    # factor test_num = m * 2^k, m is odd
    n = test_num
    b = quick_mod(randint(1, n - 1), m, n)
    if b == 1:
        return True
    for _ in range(k):
        if b == n - 1:
            return True
        else:
            b = quick_mod(b, 2, n)
    return False
```

由此封装素性检测算法如下：

```python
def primality_test(test_num, n=6):
    for _ in range(n):
        if not miller_rabin(test_num):
            return False
    return True
```

如果$n$是一个256位的数，则*Miller-Rabin*算法6次检测的错误可能性小于$1/2^{51}$，因此这里我们默认检测6次基本可以确定其素性。

## 2. 随机素数生成

使用上面的素性检测算法，我们可以生成指定比特长度的“随机”安全素数。

```python
def get_random_prime(nbits):
    r = 0
    while not ((r & 1) and primality_test(r) and primality_test(2*r+1)):
        r = randint(2 ** (nbits - 1), 2 ** nbits - 1)
    return 2 * r + 1
```

## 3. 欧几里得及其扩展算法的优化

首先给出了欧几里得算法的实现，即通过辗转相除得到最后的公因数：

```python
def gcd_classic(a: int, b: int) -> int:
    if b > a:
        a, b = b, a
    while b:
        a, b = b, a % b
    return a
```

基于辗转相除法的原理，可以进行如下改进，即二进制欧几里得算法的算法原理：

- 若$a$和$b$是偶数，则$gcd(a, b) = 2\cdot gcd(a/2, b/2)$
- 若$a$是偶数而$b$是奇数，那么$gcd(a, b) = gcd(a/2, b)$
- 若$a,b$是奇数，那么$gcd(a, b) = gcd(b, \frac{a-b}{2})$

根据原理给出下面递归形式的代码：

```python
def bin_gcd_recursion(a: int, b: int) -> int:
    if a == b:
        return a
    if b > a:
        a, b = b, a
    # since a >= b, just return a, no matter a ?= 0
    if b == 0:
        return a
    if not (a & 1):
        if not (b & 1):
            return 2 * bin_gcd_recursion(a >> 1, b >> 1)  # a even, b even
        else:
            return bin_gcd_recursion(a >> 1, b)  # a even, b odd
    else:
        if not (b & 1):
            return bin_gcd_recursion(a, b >> 1)  # a odd, b even
        else:
            return bin_gcd_recursion(b, (a - b) >> 1)  # a odd, b odd
```

而函数递归调用会频繁进行中断和堆栈相关的指令调用，效率较低，因此将算法优化为一个循环，得到如下代码：

```python
def bin_gcd_loop(a: int, b: int) -> int:
    if b > a:
        a, b = b, a
    if b == 0:
        return a
    adic = 0
    while not ((a | b) & 1):
        adic += 1
        a >>= 1
        b >>= 1
    while b:
        while not (a & 1):  # a even
            a >>= 1
        while not (b & 1):  # b even
            b >>= 1
        if b > a:
            a, b = b, a
        a, b = b, (a - b) >> 1
    return a * 2 ** adic
```

针对RSA中求解$e$的逆元$d$，首先给出使用扩展欧几里得算法求解的方法如下，得到返回的结果$x$即为$a$模$b$的逆元：

```python
def ext_gcd(a: int, b: int) -> tuple:
    if b == 0:
        return a, 1, 0
    else:
        gcd_t, x, y = ext_gcd(b, a % b)  # 递归直至余数等于0(需多递归一层用来判断)
        x, y = y, (x - (a // b) * y)  # 辗转相除法反向推导每层a、b的因子使得gcd(a,b)=ax+by成立
        return gcd_t, x, y
```

针对这个过程，也可以使用二进制的思想进行优化，得到下面的代码：

```python
def gcd_reverse(r, x, y, alpha, beta):
    if x & 1 == 0 and y & 1 == 0:
        x, y = x >> 1, y >> 1
    else:
        x, y = (x + beta) >> 1, (y - alpha) >> 1
    return r >> 1, x, y


def bin_ext_gcd(a: int, b: int)->tuple:
    d = 1
    x1, y1, x2, y2 = 1, 0, 0, 1
    while ap & 1 == 0 and bp & 1 == 0:
        ap = ap >> 1
        bp = bp >> 1
        d = d << 1
    alpha = ap
    beta = bp

    while not (ap & 1):
        ap, x1, y1 = gcd_reverse(ap, x1, y1, alpha, beta)
    while not (bp & 1):
        bp, x2, y2 = gcd_reverse(bp, x2, y2, alpha, beta)
    if ap < bp:
        ap, x1, y1, bp, x2, y2 = bp, x2, y2, ap, x1, y1
    while bp:
        ap = ap - bp
        x1, y1 = x1 - x2, y1 - y2
        while ap and (not (ap & 1)):
            ap, x1, y1 = gcd_reverse(ap, x1, y1, alpha, beta)
        if ap < bp:
            ap, x1, y1, bp, x2, y2 = bp, x2, y2, ap, x1, y1
    if a < 0:
        x1, x2 = -x1, -x2
    if b < 0:
        y1, y2 = -y1, -y2
    return d * ap, x1, y1
```

## 4. RSA参数生成

在上面几个步骤中，已经给出了一些实现基本功能的函数，使用这些函数，就可以生成需要的RSA参数。

首先指定RSA参数的比特长度`nbits`，根据其值，参数生成如下：

```python
self.p = get_random_prime(nbits=nbits)
self.q = get_random_prime(nbits=nbits)
self.n = self.p * self.q
phi_n = (self.p - 1) * (self.q - 1)
self.e = 0
while gcd(phi_n, self.e) != 1:
    self.e = randint(2 ** (len(bin(phi_n - 1)[2:]) - 1), phi_n - 1)
    self.d = invert(self.e, phi_n)
```

为防止小指数攻击，保证安全性，`get_random_prime`函数生成的素数都是安全素数，$e$的取值也要求比特长度不低于$\phi(n)$的一半。

## 5. 加解密过程实现

有了以上功能的实现，加解密的实现已经非常简洁，只需要一步快速模幂即可。

```python
quick_mod(message, self.e, self.n)  # 加密
quick_mod(ciphertext, self.d, self.n)  # 解密
```

## 6. 使用中国剩余定理优化解密过程

为了提高解密速度，可以使用中国剩余定理辅助快速模幂运算。

```python
def decrypt_CRT(ciphertext, d, p, q):
    dp = d % (p - 1)
    dq = d % (q - 1)
    m1 = quick_mod(ciphertext, dp, p)
    m2 = quick_mod(ciphertext, dq, q)
    q_inv = invert(q, p)
    h = q_inv * (m1 - m2) % p
    return (m2 + h * q) % (p * q)
```

# 四、实验结果

## 1. 公共模攻击验证

数据输入

```python
n = 114381625757888867669235779976146612010218296721242362562561842935706935245733897830597123563958705058989075147599290026879543541
e1 = 9007
e2 = 65537
m = 19050321180920251905182209030519
```

使用扩展欧几里得算法计算$s,t$，使得$e_1*s+e_2*t=gcd(e_1,e_2)=1$

根据如下公式恢复明文

$$
c_1^{s}*c_2^{t}\equiv m^{e_1*s+e_2*t}\equiv m \bmod n
$$


```python
g, s, t = ext_gcd(e1, e2)
ins1 = RSA(only_encrypt=True, key_pair={'n': n, 'e': e1})
c1 = ins1.encrypt(m)
ins2 = RSA(only_encrypt=True, key_pair={'n': n, 'e': e2})
c2 = ins2.encrypt(m)
print(quick_mod(c1, s, n) * quick_mod(c2, t, n) % n)
```

验证得到输出结果

```python
19050321180920251905182209030519
```

## 2. 不动点攻击验证

根据不动点定义，验证如下

> 称满足$m^e\equiv m \bmod n$的$m$称为不动点

```python
ins3 = RSA(only_encrypt=True, key_pair={'n': 2773, 'e': 17})
print(ins3.encrypt(2302))
```

验证得到输出结果

```python
2302
```

## 3. 程序效率分析

该部分针对自行编写的不同函数和来自`gmpy2`大数库的函数进行了效率分析，比较不同实现和优化方式的效率差异。

### 3.1 GCD效率分析

我们分别用比特长度在20，40，60，80，100规模下的同一数据集（样本数量10000）对下列几个实现进行了测试

- 欧几里得方法
- 使用函数递归实现的二进制欧几里得方法
- 使用循环实现的二进制欧几里得方法
- 来自`gmpy2`库的`gcd`函数

![gcd_algorithm_speed](C:\Users\jun\Desktop\crypto\RSA_algorithm_implementation_and_security_analysis\assets\gcd_algorithm_speed.svg)

可以发现使用二进制优化的实现函数效率有明显提升，而将递归实现转化为循环实现能使效率进一步提升，但是在40比特及以上的规模下，相比大数库中的`gcd`实现仍然有很大差距。

### 3.2 求逆元效率分析

这部分主要比较了自行编写的使用扩展欧几里得算法、二进制扩展欧几里得算法求解逆元和来自大数库的`invert`函数求解逆元的效率差异。

![invert_function_speed](C:\Users\jun\Desktop\crypto\RSA_algorithm_implementation_and_security_analysis\assets\invert_function_speed.svg)

### 3.3 随机素数生成效率分析

这部分主要比较了自行编写的*Miller-Rabin*算法和来自大数库的*Miller-Rabin*算法效率差异，可以发现自行编写的算法效率优化不足，在40比特规模下每生成200个随机的安全素数已经长达60秒，而来自大数库的*Miller-Rabin*算法在80比特规模下每生成200个随机的安全素数仅需要不足10秒。

![prime_generate_speed](C:\Users\jun\Desktop\crypto\RSA_algorithm_implementation_and_security_analysis\assets\prime_generate_speed.svg)

### 3.4 加密效率分析

由于RSA加解密涉及大量模幂运算，因此效率比较低。在下图中，比较了不同密钥长度下对同一数据（这里我们取数据长度为密钥长度减一）进行10000次加密的耗时，可以看到随密钥长度的翻倍，加密耗时也急剧增加，在1024比特长度的密钥下，加密10000次同一1023比特的数据已经达到了120秒，换算发现在1024比特长度的密钥下，加密速度仅有约12MB/s。

![RSA_encrypt_speed](C:\Users\jun\Desktop\crypto\RSA_algorithm_implementation_and_security_analysis\assets\RSA_encrypt_speed.svg)

### 3.5 中国剩余定理解密效率分析

和加密过程相同的，解密也是模幂运算。这里，我们比较了使用中国剩余定理辅助前后的解密效率，发现中国剩余定理可以显著提高解密速度。

![RSA_decrypt_speed](C:\Users\jun\Desktop\crypto\RSA_algorithm_implementation_and_security_analysis\assets\RSA_decrypt_speed.svg)

## 4. 挑战题：大数分解

使用Pallord P-1方法分解如下

```python
n=90252653600964453524559669296618135272911289775949194922543520872164147768650421038176330053599968601135821750672685664360786595430028684419411893316074286312793730822963564220564616708573764764386830123818197183233443472506106828919670406785228124876225200632055727680225997407097843708009916059133498338129
```

DEC

```python
f1=1719620105458406433483340568317543019584575635895742560438771105058321655238562613083979651479555788009994557822024565226932906295208262756822275663694111
f2=52484065122572767557293534477361686456679280880304125291106733197354892893647364164212186415880889674435558369420400890814461263958618375991691022752189839
```

HEX

```python
f1=0x20D553F6EC8DF4DD610278518BABE13E0EFD87744717F733836C634407D0230E467B622F9787080ADDE08CB349423BC93EFD965375B51F301BD9D9D25C61891F
f2=0x3EA18C437BE22139DF56AE544E1F2232C25B9C75532C15BBFCB087A6680914D4F355B0E779B6087DDB4AA938453329B6F98F91995780017FE3249B0A4D9D28D8F
```

# 五、心得体会

本次对RSA算法实现和优化的实验经历让我对RSA算法的过程和应用也有了更深层次的理解掌握。

在之前理论学习的时候，我们了解到了RSA算法的加解密的设计和实现过程，但是对其中设计细节和算法安全性不甚理解。此次实践中，对RSA加密算法的核心功能进行了复现，更加深入的认识到其设计原理，提高了理解程度。在对典型攻击实现的过程中，让我了解到RSA算法不合理的参数设置导致的潜在安全隐患；同时，在对RSA算法的优化过程中，加深了对已经学过的知识的理解和应用。

在完成实践的过程中，也遇到了一些不足和实现难点。例如在编写二进制扩展欧几里得算法时，发现对扩展欧几里得算法的原理还有理解上的欠缺，导致在实现过程中陷入困境，最终在多次排查后完成了编写工作。
