#ifndef SEGMENT_TREE_HPP   // 头文件保护，防止重复包含
#define SEGMENT_TREE_HPP

#include <vector>
#include <functional>

namespace algolib {  // 将所有内容放在命名空间中，避免与其他库冲突

template <typename T, typename Combine = std::function<T(const T&, const T&)>>
class SegmentTree {
public:
    // 构造函数：接受初始数组、合并函数（默认为加法）、单位元（默认为 T()，即 0）
    SegmentTree(const std::vector<T>& data,
                Combine combine = std::plus<T>(),
                T identity = T())
        : n(data.size()), combine(combine), identity(identity) {
        tree.resize(4 * n);          // 线段树一般需要 4 倍空间
        build(data, 1, 0, n - 1);    // 从根节点 1 开始递归建树
    }

    // 区间查询 [l, r]
    T query(int l, int r) const {
        return query(1, 0, n - 1, l, r);
    }

    // 单点更新：将位置 pos 的值改为 newVal
    void update(int pos, const T& newVal) {
        update(1, 0, n - 1, pos, newVal);
    }

    int size() const { return n; }

private:
    int n;                     // 数组大小
    std::vector<T> tree;       // 线段树数组（1-indexed）
    Combine combine;           // 合并函数对象
    T identity;                // 单位元（用于查询初始化）

    // 建树递归函数
    void build(const std::vector<T>& data, int node, int left, int right) {
        if (left == right) {                    // 叶子节点
            tree[node] = data[left];
            return;
        }
        int mid = (left + right) / 2;
        build(data, node * 2, left, mid);       // 递归左儿子
        build(data, node * 2 + 1, mid + 1, right); // 递归右儿子
        tree[node] = combine(tree[node * 2], tree[node * 2 + 1]); // 合并
    }

    // 查询递归函数
    T query(int node, int left, int right, int ql, int qr) const {
        if (ql <= left && right <= qr) {        // 当前区间完全被查询区间覆盖
            return tree[node];
        }
        int mid = (left + right) / 2;
        if (qr <= mid) {                         // 查询区间完全在左半
            return query(node * 2, left, mid, ql, qr);
        } else if (ql > mid) {                   // 查询区间完全在右半
            return query(node * 2 + 1, mid + 1, right, ql, qr);
        } else {                                  // 跨左右
            T leftRes = query(node * 2, left, mid, ql, qr);
            T rightRes = query(node * 2 + 1, mid + 1, right, ql, qr);
            return combine(leftRes, rightRes);
        }
    }

    // 更新递归函数
    void update(int node, int left, int right, int pos, const T& newVal) {
        if (left == right) {                     // 叶子节点，直接更新
            tree[node] = newVal;
            return;
        }
        int mid = (left + right) / 2;
        if (pos <= mid) {
            update(node * 2, left, mid, pos, newVal);
        } else {
            update(node * 2 + 1, mid + 1, right, pos, newVal);
        }
        tree[node] = combine(tree[node * 2], tree[node * 2 + 1]); // 重新合并
    }
};

} // namespace algolib
#endif