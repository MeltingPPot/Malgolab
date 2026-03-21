#include<iostream>
#include<random>
#include<cstdlib>
int main(int argc,char* argv[]){
    int n=(argc>1)?std::atoi(argv[1]):10;
    int max_val=(argc>2)?std::atoi(argv[2]):100;
    if(n<1) n=1;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> val_dist(1,max_val);
    std::uniform_int_distribution<int> pos_dist(0,n - 1);
    std::cout<<n<<'\n';
    for (int i=0;i<n;++i)
        std::cout<<val_dist(gen)<<" \n"[i==n-1];
    int q=(argc>3)?std::atoi(argv[3]):10;
    std::cout<<q<<'\n';
    for (int i=0;i<q;++i){
        int l=pos_dist(gen);
        int r=pos_dist(gen);
        if (l>r) std::swap(l,r);
        std::cout<<l<<' '<<r<<'\n';
    }
}
// 序列查询生成器
// [参数1]：n[参数2]：maxn[参数3]：q